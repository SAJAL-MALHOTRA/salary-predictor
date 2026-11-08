"""
test_platform.py -- Automated CI test suite for India Salary & Career Intelligence Platform.
Tests model inference, tax calculations, NLP role normalization, H1B benchmarks, and Glassdoor data.
"""

import json
from pathlib import Path
import sys
import joblib
import numpy as np
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


@pytest.fixture(scope="session")
def model_pipeline():
    pipeline_path = BASE_DIR / "salary_pipeline.pkl"
    assert pipeline_path.exists(), f"salary_pipeline.pkl not found at {pipeline_path}"
    return joblib.load(pipeline_path)


@pytest.fixture(scope="session")
def model_metadata():
    metadata_path = BASE_DIR / "model_metadata.pkl"
    assert metadata_path.exists(), f"model_metadata.pkl not found at {metadata_path}"
    return joblib.load(metadata_path)


@pytest.fixture(scope="session")
def h1b_benchmarks():
    h1b_path = BASE_DIR / "h1b_lca_benchmarks.json"
    assert h1b_path.exists(), f"h1b_lca_benchmarks.json not found at {h1b_path}"
    with open(h1b_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def glassdoor_benchmarks():
    gd_path = BASE_DIR / "glassdoor_benchmarks.json"
    assert gd_path.exists(), f"glassdoor_benchmarks.json not found at {gd_path}"
    with open(gd_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def reddit_benchmarks():
    rd_path = BASE_DIR / "reddit_benchmarks.json"
    assert rd_path.exists(), f"reddit_benchmarks.json not found at {rd_path}"
    with open(rd_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_metadata_structure(model_metadata):
    """Verify that metadata dictionary contains all expected keys and valid CV metrics."""
    expected_keys = [
        "companies",
        "company_jobs",
        "all_job_titles",
        "role_families",
        "seniority_levels",
        "cv_r2_mean",
        "cv_mae_mean",
        "cv_rmse_mean",
        "conformal_margin_80_lpa",
    ]
    for key in expected_keys:
        assert key in model_metadata, f"Missing key '{key}' in model_metadata.pkl"

    assert len(model_metadata["companies"]) >= 100, "Expected at least 100 companies"
    assert 0.35 <= model_metadata["cv_r2_mean"] <= 0.70, "CV R2 score outside realistic range"
    assert 2.0 <= model_metadata["cv_mae_mean"] <= 6.0, "CV MAE outside realistic range"
    assert 4.0 <= model_metadata["conformal_margin_80_lpa"] <= 10.0, "Conformal margin outside expected range"


def test_model_prediction(model_pipeline):
    """Test model prediction on a standard software engineering profile."""
    sample_input = pd.DataFrame(
        [
            {
                "Company": "TCS",
                "Job_Title": "Software Engineer",
                "Industry": "IT Services & Consulting",
                "Role_Family": "Software & Systems Engineering",
                "Seniority_Level": "Mid-Level",
                "Rating": 3.8,
                "Avg_Exp": 4.0,
            }
        ]
    )

    pred = model_pipeline.predict(sample_input)[0]
    assert isinstance(pred, (float, np.floating, int)), "Prediction must be numeric"
    assert 3.0 <= pred <= 20.0, f"Predicted salary {pred} LPA outside expected range for TCS 4y exp"


def test_nlp_categorization():
    """Verify regex NLP taxonomy mapping logic."""
    from taxonomy import categorize_job

    fam1, sen1 = categorize_job("Senior Software Engineer")
    assert fam1 == "Software & Systems Engineering"
    assert sen1 == "Senior / Lead"

    fam2, sen2 = categorize_job("Lead Data Scientist")
    assert fam2 == "Data Science & AI"
    assert sen2 == "Senior / Lead"

    fam3, sen3 = categorize_job("Graduate Trainee Engineer")
    assert fam3 == "Software & Systems Engineering"
    assert sen3 == "Entry / Junior"

    fam4, sen4 = categorize_job("Director of Engineering")
    assert fam4 == "Software & Systems Engineering"
    assert sen4 == "Executive / Director"


def calculate_tax_logic(ctc_lpa):
    """Independent implementation of Budget 2024 New Tax Regime for unit testing."""
    ctc = float(ctc_lpa) * 100000.0
    basic = ctc * 0.40
    epf_annual = 1800 * 12 if (basic * 0.12 > 1800 * 12 and ctc > 1500000) else basic * 0.12
    gross_salary = ctc - epf_annual
    pt_annual = 2400.0 if ctc >= 300000 else 0.0
    taxable_income = max(0.0, gross_salary - 75000.0)
    tax = 0.0
    if taxable_income > 700000.0:
        if taxable_income > 1500000.0:
            tax += (taxable_income - 1500000.0) * 0.30 + 300000.0 * 0.20 + 200000.0 * 0.15 + 300000.0 * 0.10 + 400000.0 * 0.05
        elif taxable_income > 1200000.0:
            tax += (taxable_income - 1200000.0) * 0.20 + 200000.0 * 0.15 + 300000.0 * 0.10 + 400000.0 * 0.05
        elif taxable_income > 1000000.0:
            tax += (taxable_income - 1000000.0) * 0.15 + 300000.0 * 0.10 + 400000.0 * 0.05
        elif taxable_income > 700000.0:
            tax += (taxable_income - 700000.0) * 0.10 + 400000.0 * 0.05
        tax *= 1.04
    net_annual = gross_salary - epf_annual - pt_annual - tax
    return {"net_annual": net_annual, "monthly_in_hand": net_annual / 12.0, "tax_annual": tax}


def test_tax_calculator():
    """Test Indian New Tax Regime FY 2024-25 calculations."""
    th_10 = calculate_tax_logic(10.0)
    assert 60000 <= th_10["monthly_in_hand"] <= 80000, f"Unexpected monthly in-hand: {th_10['monthly_in_hand']}"

    th_25 = calculate_tax_logic(25.0)
    assert th_25["tax_annual"] > 0, "Expected positive tax on 25 LPA CTC"
    assert th_25["monthly_in_hand"] > th_10["monthly_in_hand"], "Higher CTC must yield higher in-hand"


def test_h1b_benchmarks_data(h1b_benchmarks):
    """Verify US DOL H-1B benchmarks integrity."""
    assert len(h1b_benchmarks) >= 40, "Expected at least 40 matched H-1B employers"
    assert "TCS" in h1b_benchmarks
    assert "Infosys" in h1b_benchmarks

    tcs_h1b = h1b_benchmarks["TCS"]
    assert tcs_h1b["total_h1b_filings"] > 50000
    assert tcs_h1b["median_wage_usd"] >= 60000
    assert "Level I (Entry / Junior)" in tcs_h1b["wage_levels_usd"]


def test_glassdoor_benchmarks_data(glassdoor_benchmarks):
    """Verify Kaggle Glassdoor India benchmarks integrity."""
    assert len(glassdoor_benchmarks) >= 60, "Expected at least 60 matched Glassdoor employers"
    assert "TCS" in glassdoor_benchmarks
    assert "Infosys" in glassdoor_benchmarks
    assert "Amazon" in glassdoor_benchmarks

    tcs_gd = glassdoor_benchmarks["TCS"]
    assert tcs_gd["sample_count"] >= 100, "TCS should have >= 100 Glassdoor records"
    assert tcs_gd["median_salary_lpa"] > 0
    assert len(tcs_gd["top_locations"]) > 0


def test_reddit_benchmarks_data(reddit_benchmarks):
    """Verify r/developersIndia Reddit benchmarks integrity and dark pattern extraction."""
    assert len(reddit_benchmarks) >= 15, "Expected at least 15 benchmarked companies from Reddit"
    assert "TCS" in reddit_benchmarks
    assert "Infosys" in reddit_benchmarks
    assert "Amazon" in reddit_benchmarks

    tcs_rd = reddit_benchmarks["TCS"]
    assert tcs_rd["thread_count"] >= 1
    assert "sentiment_breakdown" in tcs_rd
    assert "red_flags" in tcs_rd
    assert tcs_rd["red_flags"]["notice_period_days"] == 90, "TCS should reflect 90-day notice period"

    amzn_rd = reddit_benchmarks["Amazon"]
    assert amzn_rd["red_flags"]["pip_quota_alert"] is True, "Amazon should detect PIP / URA quota alert"


def test_reddit_nlp_extraction():
    """Verify compensation regex and red flag parsers in reddit_nlp_extractor."""
    from reddit_nlp_extractor import extract_ctc_figures, extract_yoe, detect_red_flags

    # CTC parsing
    ctc1, base1, var1 = extract_ctc_figures("Offered 28L Base and 5L Bonus with total 34 LPA CTC")
    assert ctc1 == 34.0
    assert base1 == 28.0
    assert var1 == 5.0

    # YoE parsing
    assert extract_yoe("I have 4.5 YOE in backend") == 4.5
    assert extract_yoe("As a 2024 batch fresher looking for jobs") == 0.0

    # Red Flag detection
    flags = detect_red_flags("Management refused early release due to 90 days notice period and put team on bench")
    assert flags["notice_period_days"] == 90
    assert flags["bench_risk"] in ["Moderate", "Severe"]
    assert flags["red_flag_score"] >= 35


def test_community_notes_moderation_and_storage():
    """Verify community offer notes moderation rules, storage, and retrieval."""
    import community_notes as cn

    # 1. Moderation rules
    ok, err = cn.moderate_note("Too short")
    assert not ok and "at least 10" in err

    ok, err = cn.moderate_note("x" * 281)
    assert not ok and "exceeds 280" in err

    ok, err = cn.moderate_note("Check this out at http://scam.com/jobs")
    assert not ok and "links" in err.lower()

    ok, err = cn.moderate_note("Email me at candidate@gmail.com for details")
    assert not ok and "email" in err.lower()

    ok, err = cn.moderate_note("Call my phone at 9876543210 for referral")
    assert not ok and "phone" in err.lower()

    ok, err = cn.moderate_note("Toxic culture caused by manager named Sharma")
    assert not ok and "naming individual" in err.lower()

    valid_text = "Variable pay was paid at 75% last year. Notice period is strictly 90 days."
    ok, err = cn.moderate_note(valid_text)
    assert ok and err == ""

    # 2. Insertion and Retrieval
    test_comp = "TestCoAutomation"
    ok, msg = cn.add_note(
        company=test_comp,
        role_family="Software & Systems Engineering",
        note_text=valid_text,
        yoe=3.0,
        ctc_lpa=15.0,
        author_tag="Test Offer",
    )
    assert ok, f"Expected note insertion to succeed: {msg}"

    notes = cn.get_notes(test_comp)
    assert len(notes) >= 1
    assert notes[0]["note_text"] == valid_text
    assert notes[0]["author_tag"] == "Test Offer"

    # Clean up test row
    conn = cn.get_connection()
    with conn:
        conn.execute("DELETE FROM offer_notes WHERE company = ?", (test_comp,))
    conn.close()


def test_contract_auditor_mechanics():
    """Verify Payment of Gratuity Act 1972 statutory math, inflation gap, and contract traps."""
    import contract_auditor as ca

    # Test 12 LPA offer with 15% variable and gratuity included for 2 years tenure
    audit1 = ca.audit_offer_contract(
        ctc_lpa=12.0,
        variable_pct=15.0,
        gratuity_included=True,
        joining_bonus_lpa=1.0,
        clawback_months=12,
        notice_period_days=90,
        variable_freq="Annual",
        expected_tenure_years=2.0,
    )

    # Basic is 40% of 12L = 4.8L. Gratuity is (15/26/12)*4.8L = 23,076.92
    assert 23000 <= audit1["annual_gratuity_rupees"] <= 23100
    assert audit1["phantom_gratuity_loss_rupees"] == audit1["annual_gratuity_rupees"]
    # Guaranteed cash: 10.2L fixed - 0.23077L gratuity = ~9.97 LPA
    assert 9.90 <= audit1["guaranteed_year1_cash_lpa"] <= 10.05
    assert 16.0 <= audit1["paper_inflation_gap_pct"] <= 18.0
    assert "Section 89(1)" in audit1["clawback_flag"]
    assert "90-Day Notice Lock" in audit1["notice_flag"]

    # Test tenure >= 5 years (gratuity is not lost)
    audit2 = ca.audit_offer_contract(
        ctc_lpa=12.0,
        variable_pct=0.0,
        gratuity_included=True,
        expected_tenure_years=5.0,
    )
    assert audit2["phantom_gratuity_loss_rupees"] == 0.0
    assert audit2["guaranteed_year1_cash_lpa"] == 12.0
    assert audit2["paper_inflation_gap_pct"] == 0.0


