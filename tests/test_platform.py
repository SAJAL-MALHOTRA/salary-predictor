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


def test_company_tier_classification():
    """Verify Indian tech employer tiering and negotiation guidance rules."""
    import company_tiers as ct

    t1 = ct.classify_employer_tier("Google India")
    assert t1["tier_num"] == 1
    assert t1["typical_notice_days"] == 30
    assert "RSU" in t1["equity_structure"]

    t2 = ct.classify_employer_tier("Swiggy")
    assert t2["tier_num"] == 2
    assert "ESOP" in t2["equity_structure"]

    t3 = ct.classify_employer_tier("Thoughtworks")
    assert t3["tier_num"] == 3

    t4 = ct.classify_employer_tier("Tata Consultancy Services")
    assert t4["tier_num"] == 4
    assert t4["typical_notice_days"] == 90
    assert "band" in t4["negotiation_playbook"].lower()

    t_unk = ct.classify_employer_tier("UnknownStartup99")
    assert t_unk["tier_num"] == 3


def test_offer_parser_extraction():
    """Verify regex & heuristic parsing on typical Indian offer letter text."""
    import offer_parser as op

    sample_doc = """
    OFFER OF EMPLOYMENT
    Company: Swiggy (Bundl Technologies Pvt Ltd)
    Designation: SDE 2 - Backend
    Total CTC: INR 26,00,000 per annum
    Basic Salary: INR 10,40,000
    Variable Pay: 15% of annual CTC
    Joining Bonus: INR 3,00,000 (Subject to 12 months clawback)
    Notice Period: 60 days
    Gratuity: Included as per Payment of Gratuity Act 1972
    Variable payout: Quarterly variable disbursement
    """
    parsed = op.parse_offer_text(sample_doc)
    assert parsed["company"] == "Swiggy"
    assert "SDE 2" in parsed["role"]
    assert parsed["ctc_lpa"] == 26.0
    assert parsed["variable_pct"] == 15
    assert parsed["joining_bonus_lpa"] == 3.0
    assert parsed["clawback_months"] == 12
    assert parsed["notice_period_days"] == 60
    assert parsed["gratuity_included"] is True
    assert "Quarterly" in parsed["variable_freq"]
    assert parsed["confidence"] >= 0.70


def test_equity_engine_mechanics():
    """Verify RSU & ESOP vesting schedules, exercise traps, and Section 17(2) perquisite tax."""
    import equity_engine as ee

    # Test Public Tech RSU grant ($40,000 ~ 32 LPA total 4-year grant)
    rsu_res = ee.evaluate_equity_component(
        equity_type="RSU",
        grant_value_lpa=32.0,
        vesting_schedule="Standard 25/25/25/25",
        company_stage="Public Tech / GCC",
        exercise_window_days=90,
        annual_base_ctc_lpa=28.0,
    )
    assert rsu_res["y1_vest_lpa"] == 8.0
    assert rsu_res["liquidity_factor"] == 1.00
    assert rsu_res["total_y1_quoted_rewards_lpa"] == 36.0
    assert "Public RSU Grant" in rsu_res["exercise_trap_flags"][0]

    # Test Startup ESOP with 90-day exercise trap
    esop_res = ee.evaluate_equity_component(
        equity_type="ESOP",
        grant_value_lpa=20.0,
        vesting_schedule="Standard 25/25/25/25",
        company_stage="Late-Stage Unicorn (Frequent Buybacks)",
        exercise_window_days=90,
        annual_base_ctc_lpa=20.0,
    )
    assert esop_res["y1_vest_lpa"] == 5.0
    assert esop_res["liquidity_factor"] == 0.65
    assert esop_res["y1_realizable_lpa"] == 3.25
    assert "90-Day Golden Handcuffs Trap" in esop_res["exercise_trap_flags"][0]


def test_decision_matrix_comparisons():
    """Verify multi-offer comparative scoring, monthly take-home delta, and notice buyout timeline."""
    import decision_matrix as dm

    # Offer A: 12 LPA, 100% cash, 90-day notice, Tier 4
    prof_a = dm.evaluate_offer_profile(
        name="Offer A (TCS)",
        ctc_lpa=12.0,
        variable_pct=15.0,
        joining_bonus_lpa=0.0,
        notice_period_days=90,
        gratuity_included=True,
        expected_tenure_years=2.0,
        take_home_monthly=78000,
        guaranteed_year1_cash_lpa=9.97,
        tier_num=4,
    )
    # Offer B: 24 LPA, 15% variable, 30-day notice, Tier 1
    prof_b = dm.evaluate_offer_profile(
        name="Offer B (Google)",
        ctc_lpa=24.0,
        variable_pct=15.0,
        joining_bonus_lpa=3.0,
        notice_period_days=30,
        gratuity_included=False,
        expected_tenure_years=2.0,
        take_home_monthly=145000,
        guaranteed_year1_cash_lpa=20.4,
        tier_num=1,
    )

    comp = dm.compare_two_offers(prof_a, prof_b)
    assert comp["diff_monthly"] == 67000
    assert comp["diff_annual_net"] == 67000 * 12
    assert comp["diff_guaranteed_lpa"] > 10.0
    assert prof_b["mobility_score"] > prof_a["mobility_score"]
    assert "Offer B" in comp["verdict_title"]


def test_negotiation_war_room_playbooks():
    """Verify recruiter objection playbooks have complete email and verbal scripts."""
    import negotiation_war_room as nwr

    playbooks = nwr.get_all_objections()
    assert len(playbooks) == 5

    for p in playbooks:
        assert "email_script" in p and len(p["email_script"]) > 100
        assert "verbal_script" in p and len(p["verbal_script"]) > 50
        assert "winning_leverage" in p and len(p["winning_leverage"]) > 20

    hike_cap = nwr.get_objection_by_id("hike_cap")
    assert "20%" in hike_cap["title"]


def test_executive_pdf_memo_generation():
    """Verify ReportLab generation of 2-page executive Offer Audit Memo."""
    import report_generator as rg

    pdf_bytes = rg.generate_pdf_audit_memo(
        offer_data={"company": "Infosys", "role": "Senior Engineer", "exp": 3.5, "city": "Bangalore", "ctc_lpa": 12.0, "variable_pct": 15},
        take_home_data={"low_mo": 75000, "high_mo": 88000, "th_100": {"ctc": 1200000, "basic": 480000, "gross": 1200000, "tax_annual": 75000, "epf_annual": 57600, "pt_annual": 2400, "net_annual": 1000000}},
        contract_audit={"structured_risks": [], "paper_inflation_gap_pct": 17.0, "paper_inflation_gap_rupees": 204000, "guaranteed_year1_cash_lpa": 9.96},
        market_data={"percentile": 55, "family": "Software Engineering", "tier_badge": "Tier 4", "p25": 10.0, "p50": 13.5, "p75": 17.0, "conf_low": 6.0, "conf_high": 18.0},
        counter_data={"c_cons": 13.0, "c_targ": 14.5, "c_strt": 16.5},
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")




