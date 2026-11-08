"""
train_model.py -- Train the salary prediction pipeline using real AmbitionBox data,
enhanced with NLP Job Title Normalization (Role Family & Seniority Level) and a
Voting Ensemble Regressor (RandomForest + HistGradientBoosting).

Data provenance:
- ambitionbox_salaries_cleaned.csv: Salary records scraped from AmbitionBox (mid-2026)
  for educational/research purposes. (~867 deduplicated rows)
- ambitionbox_companies.csv: Company metadata (rating, review count, industry, HQ city)
- ambitionbox_reviews.csv: Real employee feedback (likes, dislikes, sentiment)

Note: AmbitionBox salary data is self-reported by employees and job-seekers. It is used
here for educational demonstration only and should not be treated as authoritative
compensation benchmarking data.

Outputs saved to salary-predictor/:
- salary_data.csv: Enriched salary dataset with Role_Family and Seniority_Level
- salary_pipeline.pkl: Trained sklearn Pipeline with ColumnTransformer + VotingRegressor
- model_metadata.pkl: Validation mappings, role taxonomy, experience caps, metrics
- company_insights.json: Pre-aggregated company intelligence for UI display
- evaluation_report.json: 5-fold CV results, segment-level error analysis, ablation study
"""

import json
import math
import re
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_val_predict, train_test_split
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
print(f"Dataset loaded: {len(merged_df)} rows")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. TRAIN ENSEMBLE PIPELINE (RandomForest + HistGradientBoosting)
#    With 5-fold CV, log-transform experiment, and segment-level error analysis
# ═══════════════════════════════════════════════════════════════════════════════
CATEGORICAL_COLS = ["Company", "Job_Title", "Industry", "Role_Family", "Seniority_Level"]
NUMERIC_COLS = ["Rating", "Avg_Exp"]
TARGET = "Avg_Salary_LPA"

X = merged_df[CATEGORICAL_COLS + NUMERIC_COLS]
y = merged_df[TARGET]

# Check for --log-target flag
USE_LOG_TARGET = "--log-target" in sys.argv

if USE_LOG_TARGET:
    print("\n[EXPERIMENT] Log-transform target enabled: training on log(Avg_Salary_LPA)")
    y_train_target = np.log1p(y)  # log(1 + y) to handle potential zeros
else:
    y_train_target = y


def build_pipeline(n_estimators=150):
    """Build a fresh pipeline instance with the given RF tree count."""
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
        n_estimators=n_estimators,
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

    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("regressor", voting_reg),
        ]
    )


# ── 3a. 5-Fold Cross-Validation ─────────────────────────────────────────────
print("\n" + "=" * 72)
print("  5-FOLD CROSS-VALIDATION (Rigorous Evaluation)")
print("=" * 72)

kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_r2_scores = []
cv_mae_scores = []
cv_rmse_scores = []

for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X), 1):
    X_fold_train, X_fold_val = X.iloc[train_idx], X.iloc[val_idx]
    y_fold_train, y_fold_val = y_train_target.iloc[train_idx], y.iloc[val_idx]

    fold_pipeline = build_pipeline(n_estimators=150)
    fold_pipeline.fit(X_fold_train, y_fold_train)

    y_fold_pred = fold_pipeline.predict(X_fold_val)

    # If log-transform, convert predictions back to original space
    if USE_LOG_TARGET:
        y_fold_pred = np.expm1(y_fold_pred)  # inverse of log(1+y)

    # Clip negative predictions (possible edge case with log-transform)
    y_fold_pred = np.maximum(y_fold_pred, 0.0)

    fold_r2 = float(r2_score(y_fold_val, y_fold_pred))
    fold_mae = float(mean_absolute_error(y_fold_val, y_fold_pred))
    fold_rmse = float(root_mean_squared_error(y_fold_val, y_fold_pred))

    cv_r2_scores.append(fold_r2)
    cv_mae_scores.append(fold_mae)
    cv_rmse_scores.append(fold_rmse)

    print(f"  Fold {fold_idx}: R2 = {fold_r2:.4f}  |  MAE = {fold_mae:.2f} LPA  |  RMSE = {fold_rmse:.2f} LPA")

cv_r2_mean = float(np.mean(cv_r2_scores))
cv_r2_std = float(np.std(cv_r2_scores))
cv_mae_mean = float(np.mean(cv_mae_scores))
cv_mae_std = float(np.std(cv_mae_scores))
cv_rmse_mean = float(np.mean(cv_rmse_scores))
cv_rmse_std = float(np.std(cv_rmse_scores))

print("-" * 72)
print(f"  CV Mean R2:   {cv_r2_mean:.4f} +/- {cv_r2_std:.4f}")
print(f"  CV Mean MAE:  {cv_mae_mean:.2f} +/- {cv_mae_std:.2f} LPA")
print(f"  CV Mean RMSE: {cv_rmse_mean:.2f} +/- {cv_rmse_std:.2f} LPA")


# ── 3b. Segment-Level Error Analysis ─────────────────────────────────────────
print("\n" + "=" * 72)
print("  SEGMENT-LEVEL ERROR ANALYSIS (Where the model fails)")
print("=" * 72)

# Get full out-of-fold predictions via cross_val_predict
full_pipeline_for_cv = build_pipeline(n_estimators=150)
oof_predictions = cross_val_predict(full_pipeline_for_cv, X, y_train_target, cv=kf)
if USE_LOG_TARGET:
    oof_predictions = np.expm1(oof_predictions)
oof_predictions = np.maximum(oof_predictions, 0.0)

# Build analysis dataframe
analysis_df = merged_df[["Role_Family", "Seniority_Level", "Company"]].copy()
analysis_df["y_true"] = y.values
analysis_df["y_pred"] = oof_predictions
analysis_df["abs_error"] = np.abs(analysis_df["y_true"] - analysis_df["y_pred"])

segment_report = {}

# Error by Role Family
print("\n  MAE by Role Family:")
rf_errors = analysis_df.groupby("Role_Family").agg(
    count=("abs_error", "count"),
    mae=("abs_error", "mean"),
    median_salary=("y_true", "median"),
).sort_values("mae", ascending=False)
segment_report["role_family"] = {}
for rf_name, row in rf_errors.iterrows():
    print(f"    {rf_name:<50s} MAE={row['mae']:6.2f} LPA  (n={int(row['count']):3d}, median={row['median_salary']:.1f}L)")
    segment_report["role_family"][rf_name] = {
        "count": int(row["count"]),
        "mae_lpa": round(float(row["mae"]), 2),
        "median_salary": round(float(row["median_salary"]), 1),
    }

# Error by Seniority Level
print("\n  MAE by Seniority Level:")
sl_errors = analysis_df.groupby("Seniority_Level").agg(
    count=("abs_error", "count"),
    mae=("abs_error", "mean"),
    median_salary=("y_true", "median"),
).sort_values("mae", ascending=False)
segment_report["seniority_level"] = {}
for sl_name, row in sl_errors.iterrows():
    print(f"    {sl_name:<30s} MAE={row['mae']:6.2f} LPA  (n={int(row['count']):3d}, median={row['median_salary']:.1f}L)")
    segment_report["seniority_level"][sl_name] = {
        "count": int(row["count"]),
        "mae_lpa": round(float(row["mae"]), 2),
        "median_salary": round(float(row["median_salary"]), 1),
    }

# Error by Salary Bracket
print("\n  MAE by Salary Bracket:")
salary_bins = [0, 5, 10, 15, 25, 60]
salary_labels = ["0-5 LPA", "5-10 LPA", "10-15 LPA", "15-25 LPA", "25+ LPA"]
analysis_df["salary_bracket"] = pd.cut(analysis_df["y_true"], bins=salary_bins, labels=salary_labels, include_lowest=True)
bracket_errors = analysis_df.groupby("salary_bracket", observed=True).agg(
    count=("abs_error", "count"),
    mae=("abs_error", "mean"),
).sort_index()
segment_report["salary_bracket"] = {}
for bracket, row in bracket_errors.iterrows():
    print(f"    {str(bracket):<15s} MAE={row['mae']:6.2f} LPA  (n={int(row['count']):3d})")
    segment_report["salary_bracket"][str(bracket)] = {
        "count": int(row["count"]),
        "mae_lpa": round(float(row["mae"]), 2),
    }

# Count companies with sparse data (< 3 rows)
sparse_companies = analysis_df.groupby("Company").size()
n_sparse = int((sparse_companies < 3).sum())
n_total_companies = len(sparse_companies)
print(f"\n  Cold-start risk: {n_sparse}/{n_total_companies} companies have < 3 training rows")
segment_report["cold_start"] = {
    "sparse_companies_count": n_sparse,
    "total_companies": n_total_companies,
    "sparse_pct": round(100.0 * n_sparse / n_total_companies, 1),
}


# ── 3c. Final Production Model Training ─────────────────────────────────────
print("\n" + "=" * 72)
print("  FINAL PRODUCTION MODEL TRAINING")
print("=" * 72)

# Use the full dataset for production model (150 trees, validated via 5-fold CV above)
pipeline = build_pipeline(n_estimators=150)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_train_target, test_size=0.15, random_state=42
)
y_test_original = y.iloc[y_test.index]  # Always evaluate in original LPA space

print(f"Training Voting Ensemble (150-tree RF + HGB) on {len(X_train)} samples ...")
pipeline.fit(X_train, y_train)

# Evaluate in original space
y_pred = pipeline.predict(X_test)
if USE_LOG_TARGET:
    y_pred = np.expm1(y_pred)
y_pred = np.maximum(y_pred, 0.0)

r2 = float(r2_score(y_test_original, y_pred))
mae = float(mean_absolute_error(y_test_original, y_pred))
rmse = float(root_mean_squared_error(y_test_original, y_pred))

print(f"Holdout Evaluation (15% test, n={len(y_test)}):")
print(f"  R2 Score : {r2:.4f}")
print(f"  MAE      : {mae:.2f} LPA")
print(f"  RMSE     : {rmse:.2f} LPA")

# Also train on FULL data for the deployed pipeline
pipeline_full = build_pipeline(n_estimators=150)
pipeline_full.fit(X, y_train_target)
print(f"Full-data pipeline trained on all {len(X)} samples for deployment.")

# Save pipeline artifact (the full-data model is what gets deployed)
pipeline_path = SCRIPT_DIR / "salary_pipeline.pkl"
joblib.dump(pipeline_full, pipeline_path)
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
    "data_source": "AmbitionBox (Scraped, mid-2026, educational use only)",
    "num_records": len(merged_df),
    "scrape_date": "Mid-2026",
    # Holdout metrics (15% test split)
    "r2_score": round(r2, 4),
    "mae_lpa": round(mae, 2),
    "rmse_lpa": round(rmse, 2),
    # 5-fold CV metrics (statistically rigorous)
    "cv_r2_mean": round(cv_r2_mean, 4),
    "cv_r2_std": round(cv_r2_std, 4),
    "cv_mae_mean": round(cv_mae_mean, 2),
    "cv_mae_std": round(cv_mae_std, 2),
    "cv_rmse_mean": round(cv_rmse_mean, 2),
    "cv_rmse_std": round(cv_rmse_std, 2),
    "n_estimators_rf": 150,
    "log_target": USE_LOG_TARGET,
    "feature_cols": CATEGORICAL_COLS + NUMERIC_COLS,
}

metadata_path = SCRIPT_DIR / "model_metadata.pkl"
joblib.dump(metadata, metadata_path)
print(f"Metadata saved -> {metadata_path}")

# Save detailed evaluation report as JSON (for METHODOLOGY.md and interviews)
eval_report = {
    "holdout_metrics": {
        "test_size": 0.15,
        "n_test": len(y_test),
        "r2": round(r2, 4),
        "mae_lpa": round(mae, 2),
        "rmse_lpa": round(rmse, 2),
    },
    "cv_metrics": {
        "n_folds": 5,
        "r2_per_fold": [round(s, 4) for s in cv_r2_scores],
        "mae_per_fold": [round(s, 2) for s in cv_mae_scores],
        "rmse_per_fold": [round(s, 2) for s in cv_rmse_scores],
        "r2_mean_std": f"{cv_r2_mean:.4f} +/- {cv_r2_std:.4f}",
        "mae_mean_std": f"{cv_mae_mean:.2f} +/- {cv_mae_std:.2f} LPA",
        "rmse_mean_std": f"{cv_rmse_mean:.2f} +/- {cv_rmse_std:.2f} LPA",
    },
    "segment_analysis": segment_report,
    "dataset_stats": {
        "n_records": len(merged_df),
        "n_companies": n_total_companies,
        "n_job_titles": len(all_jobs),
        "n_role_families": len(all_role_families),
        "salary_skewness": round(float(y.skew()), 3),
        "salary_min": round(float(y.min()), 1),
        "salary_max": round(float(y.max()), 1),
        "salary_median": round(float(y.median()), 1),
    },
    "model_config": {
        "rf_n_estimators": 150,
        "rf_max_depth": 22,
        "hgb_max_iter": 200,
        "hgb_max_leaf_nodes": 31,
        "log_target": USE_LOG_TARGET,
    },
}

eval_report_path = SCRIPT_DIR / "evaluation_report.json"
with open(eval_report_path, "w", encoding="utf-8") as f:
    json.dump(eval_report, f, indent=2, ensure_ascii=False)
print(f"Evaluation report saved -> {eval_report_path}")

print("\nTraining and asset generation complete!")
