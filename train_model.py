"""
train_model.py -- Train the salary prediction pipeline using real AmbitionBox data,
enhanced with NLP Job Title Normalization (Role Family & Seniority Level) and a
Voting Ensemble Regressor (RandomForest + HistGradientBoosting).

Data sources:
- ambitionbox_salaries_cleaned.csv: Salary records (~867 deduplicated rows)
- ambitionbox_companies.csv: Company metadata (rating, review count, industry, HQ city)
- ambitionbox_reviews.csv: Real employee feedback (likes, dislikes, sentiment)

Outputs saved to salary-predictor/:
- salary_data.csv: Enriched salary dataset with Role_Family and Seniority_Level
- salary_pipeline.pkl: Trained sklearn Pipeline with ColumnTransformer + VotingRegressor
- model_metadata.pkl: Validation mappings, role taxonomy, experience caps, metrics
- company_insights.json: Pre-aggregated company intelligence for UI display
"""

import json
import math
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# ── Directories ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
SCRAPING_DIR = Path(r"C:\Users\2006s\web_scraping")

SALARIES_FILE = SCRAPING_DIR / "ambitionbox_salaries_cleaned.csv"
COMPANIES_FILE = SCRAPING_DIR / "ambitionbox_companies.csv"
REVIEWS_FILE = SCRAPING_DIR / "ambitionbox_reviews.csv"

# ═══════════════════════════════════════════════════════════════════════════════
# 1. NLP JOB TITLE NORMALIZATION TAXONOMY
# ═══════════════════════════════════════════════════════════════════════════════
def categorize_job(title: str):
    """
    Map noisy, scraped job headlines into canonical Role Family & Seniority Level.
    """
    t = str(title).lower()

    # Seniority Level
    seniority = "Mid-Level"
    if re.search(r"\b(intern|trainee|fresher|graduate|entry|junior|jr|assistant|associate 1|l1)\b", t) and not re.search(
        r"\b(senior|sr|lead|vp|avp|director|manager|head)\b", t
    ):
        seniority = "Entry / Junior"
    elif re.search(r"\b(vp|vice president|avp|director|head|general manager|cxo|cto|cfo|partner)\b", t):
        seniority = "Executive / Director"
    elif re.search(r"\b(senior|sr|lead|principal|architect|specialist|tech lead|team lead|staff|supervisor)\b", t):
        seniority = "Senior / Lead"
    elif re.search(r"\b(manager|program manager|project manager)\b", t):
        seniority = "Manager / Lead"

    # Role Family
    if re.search(r"\b(data scientist|ai|ml|machine learning|deep learning|nlp|computer vision|ai/ml)\b", t):
        role_family = "Data Science & AI"
    elif re.search(r"\b(data engineer|big data|etl|bi|data analyst|business analyst|data modeler|analytics|alteryx|data platform|data)\b", t):
        role_family = "Data & Analytics"
    elif re.search(r"\b(frontend|front-end|react|angular|vue|ui developer|android|ios|mobile|flutter|react native)\b", t):
        role_family = "Frontend & Mobile Engineering"
    elif re.search(r"\b(devops|sre|cloud|aws|azure|gcp|infrastructure|system admin|linux|docker|kubernetes|security|cyber|network|soc|penetration|infosec|edr|iam|identity)\b", t):
        role_family = "Cloud, DevOps & Cybersecurity"
    elif re.search(r"\b(qa|testing|test engineer|automation|quality assurance|sdet|test|quality)\b", t):
        role_family = "QA & Quality Engineering"
    elif re.search(r"\b(fullstack|full-stack|full stack|web developer|backend|back-end|java|python|c\+\+|\.net|node|golang|c#|spring boot|software engineer|software developer|programmer|coder|sde|developer|solution architect|application engineer|engineer|technical)\b", t):
        role_family = "Software & Systems Engineering"
    elif re.search(r"\b(sap|salesforce|servicenow|oracle|erp|peoplesoft|abap|crm|packaged|consultant)\b", t):
        role_family = "Enterprise Solutions & Consulting (SAP/ERP)"
    elif re.search(r"\b(product manager|product owner|ui/ux|ux designer|product design|project manager|program manager|scrum)\b", t):
        role_family = "Product & Project Management"
    elif re.search(r"\b(sales|business development|bde|bda|account executive|relationship manager|client relationship|tele sales|inside sales|territory|agency development|merchant|acquisition|store|officer)\b", t):
        role_family = "Sales, BD & Client Relations"
    elif re.search(r"\b(marketing|seo|growth|content|digital marketing|brand|social media|campaign|market)\b", t):
        role_family = "Marketing & Communications"
    elif re.search(r"\b(finance|accountant|accounts|audit|tax|treasury|financial|banking|credit|underwriter|loan|branch manager|collection|fund|settlement|payroll)\b", t):
        role_family = "Finance, Banking & Accounting"
    elif re.search(r"\b(hr|human resources|recruiter|talent acquisition|people ops)\b", t):
        role_family = "Human Resources"
    elif re.search(r"\b(customer support|customer service|customer success|bpo|call center|telecaller|voice|support|desk|helpdesk|chat|inbound|outbound|process)\b", t):
        role_family = "Customer Support & BPO Operations"
    elif re.search(r"\b(operations|supply chain|logistics|warehouse|procurement|service manager|team lead|planning)\b", t):
        role_family = "Operations & Supply Chain"
    else:
        role_family = "General Corporate & Services"

    return role_family, seniority


# ═══════════════════════════════════════════════════════════════════════════════
# 2. LOAD & PREPARE REAL DATA
# ═══════════════════════════════════════════════════════════════════════════════
local_csv = SCRIPT_DIR / "salary_data.csv"

if SALARIES_FILE.exists() and COMPANIES_FILE.exists():
    print(f"Loading raw data from {SCRAPING_DIR} ...")
    sal_raw = pd.read_csv(SALARIES_FILE)
    comp_raw = pd.read_csv(COMPANIES_FILE)
    rev_raw = pd.read_csv(REVIEWS_FILE) if REVIEWS_FILE.exists() else pd.DataFrame()

    def _parse_comp_info(row):
        tl = str(row.get("Type/Location", ""))
        parts = [p.strip() for p in tl.split("|")]
        industry = parts[0] if len(parts) > 0 and parts[0] else "Corporate"
        loc_part = parts[1] if len(parts) > 1 and parts[1] else "India"
        city = loc_part.split("+")[0].strip() if "+" in loc_part else loc_part.strip()
        return pd.Series({"Industry": industry, "HQ_City": city})

    parsed = comp_raw.apply(_parse_comp_info, axis=1)
    comp_clean = comp_raw.copy()
    comp_clean["Industry"] = parsed["Industry"]
    comp_clean["HQ_City"] = parsed["HQ_City"]
    comp_clean["Rating"] = pd.to_numeric(comp_clean["Rating"], errors="coerce").fillna(3.5)

    sal_df = sal_raw.drop_duplicates(
        subset=["Company", "Job_Title", "Avg_Exp", "Avg_Salary_LPA"]
    ).copy()
    sal_df = sal_df[sal_df["Avg_Salary_LPA"] > 0].reset_index(drop=True)

    role_meta = sal_df["Job_Title"].apply(lambda x: pd.Series(categorize_job(x), index=["Role_Family", "Seniority_Level"]))
    sal_df["Role_Family"] = role_meta["Role_Family"]
    sal_df["Seniority_Level"] = role_meta["Seniority_Level"]

    merged_df = sal_df.merge(
        comp_clean[["Name", "Rating", "Reviews", "Industry", "HQ_City"]],
        left_on="Company",
        right_on="Name",
        how="left",
    )
    merged_df["Rating"] = merged_df["Rating"].fillna(3.5)
    merged_df["Industry"] = merged_df["Industry"].fillna("Corporate")
    merged_df["HQ_City"] = merged_df["HQ_City"].fillna("India")
    merged_df.to_csv(local_csv, index=False)
    print(f"Enriched salary records saved -> {local_csv} ({len(merged_df)} rows)")
elif local_csv.exists():
    print(f"Loading existing enriched dataset from {local_csv} ...")
    merged_df = pd.read_csv(local_csv)
    rev_raw = pd.DataFrame()
else:
    raise FileNotFoundError(f"Neither {SALARIES_FILE} nor {local_csv} could be found!")
print(f"Enriched salary records saved -> {out_csv} ({len(merged_df)} rows)")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. TRAIN ENSEMBLE PIPELINE (RandomForest + HistGradientBoosting)
# ═══════════════════════════════════════════════════════════════════════════════
CATEGORICAL_COLS = ["Company", "Job_Title", "Industry", "Role_Family", "Seniority_Level"]
NUMERIC_COLS = ["Rating", "Avg_Exp"]
TARGET = "Avg_Salary_LPA"

X = merged_df[CATEGORICAL_COLS + NUMERIC_COLS]
y = merged_df[TARGET]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=2),
            CATEGORICAL_COLS,
        ),
    ],
    remainder="passthrough",  # Rating and Avg_Exp pass through
)

rf_reg = RandomForestRegressor(
    n_estimators=400,
    max_depth=22,
    min_samples_split=3,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)

hgb_reg = HistGradientBoostingRegressor(
    max_iter=200,
    max_leaf_nodes=31,
    min_samples_leaf=3,
    random_state=42,
)

voting_reg = VotingRegressor(
    estimators=[
        ("rf", rf_reg),
        ("hgb", hgb_reg),
    ]
)

pipeline = Pipeline(
    [
        ("preprocessor", preprocessor),
        ("regressor", voting_reg),
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42
)

print(f"Training Voting Ensemble (RandomForest + HistGradientBoosting) on {len(X_train)} samples ...")
pipeline.fit(X_train, y_train)

# Evaluation
y_pred = pipeline.predict(X_test)
r2 = float(r2_score(y_test, y_pred))
mae = float(mean_absolute_error(y_test, y_pred))
rmse = float(root_mean_squared_error(y_test, y_pred))

print(f"Model Evaluation on Holdout:")
print(f"  R2 Score : {r2:.4f}")
print(f"  MAE      : {mae:.2f} LPA")
print(f"  RMSE     : {rmse:.2f} LPA")

# Save pipeline artifact
pipeline_path = SCRIPT_DIR / "salary_pipeline.pkl"
joblib.dump(pipeline, pipeline_path)
print(f"Pipeline saved -> {pipeline_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. BUILD COMPANY INSIGHTS & METADATA
# ═══════════════════════════════════════════════════════════════════════════════
companies_list = sorted(merged_df["Company"].unique().tolist())
company_jobs = {}
for comp in companies_list:
    company_jobs[comp] = sorted(
        merged_df[merged_df["Company"] == comp]["Job_Title"].unique().tolist()
    )

all_jobs = sorted(merged_df["Job_Title"].unique().tolist())
all_role_families = sorted(merged_df["Role_Family"].unique().tolist())
all_seniorities = ["Entry / Junior", "Mid-Level", "Senior / Lead", "Manager / Lead", "Executive / Director"]
experience_cap = math.ceil(float(merged_df["Avg_Exp"].quantile(0.99)) * 2) / 2

# Company intelligence dictionary
company_insights = {}
for comp in companies_list:
    comp_sub = merged_df[merged_df["Company"] == comp]
    rating_val = float(comp_sub["Rating"].iloc[0])
    reviews_str = str(comp_sub["Reviews"].iloc[0])
    industry_str = str(comp_sub["Industry"].iloc[0])
    hq_str = str(comp_sub["HQ_City"].iloc[0])

    # Extract sample likes & dislikes from reviews
    likes = []
    dislikes = []
    if len(rev_raw) > 0:
        c_revs = rev_raw[rev_raw["Company"] == comp]
        if len(c_revs) > 0:
            valid_likes = c_revs["Likes"].dropna().astype(str)
            valid_likes = valid_likes[valid_likes.str.len() > 30].drop_duplicates()
            likes = valid_likes.head(3).tolist()

            valid_dislikes = c_revs["Dislikes"].dropna().astype(str)
            valid_dislikes = valid_dislikes[valid_dislikes.str.len() > 30].drop_duplicates()
            dislikes = valid_dislikes.head(3).tolist()

    company_insights[comp] = {
        "rating": rating_val,
        "reviews": reviews_str,
        "industry": industry_str,
        "hq_city": hq_str,
        "salary_records_count": len(comp_sub),
        "median_salary": round(float(comp_sub["Avg_Salary_LPA"].median()), 1),
        "min_salary": round(float(comp_sub["Avg_Salary_LPA"].min()), 1),
        "max_salary": round(float(comp_sub["Avg_Salary_LPA"].max()), 1),
        "top_likes": likes,
        "top_dislikes": dislikes,
    }

# Save company insights as JSON
insights_path = SCRIPT_DIR / "company_insights.json"
with open(insights_path, "w", encoding="utf-8") as f:
    json.dump(company_insights, f, indent=2, ensure_ascii=False)
print(f"Company insights saved -> {insights_path}")

# Metadata artifact
metadata = {
    "companies": companies_list,
    "company_jobs": company_jobs,
    "all_job_titles": all_jobs,
    "role_families": all_role_families,
    "seniority_levels": all_seniorities,
    "experience_cap": experience_cap,
    "data_source": "AmbitionBox (Scraped)",
    "num_records": len(merged_df),
    "scrape_date": "Mid-2026",
    "r2_score": round(r2, 4),
    "mae_lpa": round(mae, 2),
    "rmse_lpa": round(rmse, 2),
    "feature_cols": CATEGORICAL_COLS + NUMERIC_COLS,
}

metadata_path = SCRIPT_DIR / "model_metadata.pkl"
joblib.dump(metadata, metadata_path)
print(f"Metadata saved -> {metadata_path}")
print("Training and asset generation complete!")
