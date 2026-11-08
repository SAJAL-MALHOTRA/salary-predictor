# 🇮🇳 India Salary & Career Intelligence Platform

[![CI Test Suite](https://github.com/SAJAL-MALHOTRA/salary-predictor/actions/workflows/ci.yml/badge.svg)](https://github.com/SAJAL-MALHOTRA/salary-predictor/actions/workflows/ci.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
![Python 3.11 | 3.12](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Voting%20Ensemble-F7931E?logo=scikit-learn&logoColor=white)
![FAISS Vector Index](https://img.shields.io/badge/FAISS-33k%20Vectors-0468FF?logo=meta&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

A production-grade compensation and career intelligence platform combining **Voting Ensemble Machine Learning (RF + HGB)**, **Retrieval-Augmented Generation (FAISS + Gemini/Extractive RAG)**, **NLP Role Taxonomy Normalization**, and **Multi-Source Cross-Validation (AmbitionBox + Kaggle Glassdoor India + US DOL OFLC H-1B Disclosures)**.

> 📖 **Deep Dive Technical Report:** Read the complete [Machine Learning Methodology, Cross-Validation & Ablation Report](METHODOLOGY.md) for 5-fold CV breakdowns, segment-level error analysis, log-transform trade-offs, and cold-start shrinkage.

---

## 🚀 Key Modules & Capabilities

### 1. 🎯 Precision Salary Estimation with Voting Ensemble
- **Ensemble Architecture:** `sklearn.pipeline.Pipeline` with `ColumnTransformer` + `VotingRegressor`:
  - **Estimator 1:** `RandomForestRegressor` (150 estimators, max depth 22, min samples split 3).
  - **Estimator 2:** `HistGradientBoostingRegressor` (200 iterations, 31 max leaves).
- **Rigorous Evaluation:**
  - **5-Fold Cross-Validation:** **$R^2 = 0.4993 \pm 0.0620$** | $\text{MAE} = 3.95 \pm 0.18\text{ LPA}$ | $\text{RMSE} = 6.45 \pm 0.45\text{ LPA}$
  - Single 15% holdout reported as secondary check ($R^2 = 0.5661$, $\text{MAE} = 3.84\text{ LPA}$), not headline.
- Outputs **80% Conformal Prediction Intervals** ($\pm 6.01\text{ LPA}$, certified 80.0% coverage) alongside tree-variance bands (71.2% empirical OOF coverage).
- Displays verified **AmbitionBox ground-truth min/max/mean ranges** when exact matches exist.
- Surfaces **Cold-Start confidence notices** when an employer has $< 3$ records on file.

### 2. 🏷️ NLP Role Family & Seniority Normalization
- Automatically maps 750+ noisy, scraped job headlines into **15 Canonical Role Families**:
  - *Data Science & AI, Data & Analytics, Frontend & Mobile, Software & Systems Engineering, Cloud/DevOps & Cybersecurity, QA & Testing, Enterprise Solutions (SAP/SF), Product & Project Management, Sales & BD, Marketing, Finance & Banking, HR, Customer Support & BPO, Operations & Supply Chain, General Corporate.*
- Detects **5 Seniority Levels**: *Entry / Junior, Mid-Level, Senior / Lead, Manager / Lead, Executive / Director*.
- Enhances model generalization and enables browsing roles by functional domain.

### 3. 🤖 Ask AmbitionBox AI: RAG Review Assistant
- Embedded **33,200+ employee review vectors** using `all-MiniLM-L6-v2` and indexed with **FAISS**.
- Allows users to ask natural questions like:
  - *"How is the work-life balance and client management at TCS?"*
  - *"Are salary hikes and appraisals fair at Flipkart compared to other product companies?"*
  - *"What do freshers say about the bench period and learning curve?"*
- **Two-tier Intelligence Engine:**
  - **Generative AI:** Powers synthesis using Google Gemini when an API key is provided.
  - **Local Semantic AI Fallback:** Zero-API, instant extractive synthesis with verified review quotes and ratings.

### 4. 🏢 Deep Company Intelligence & Employee Voice
- Enriched with metadata from 10,000+ company profiles: **AmbitionBox Rating (out of 5.0)**, **Total Reviews**, **Industry**, and **HQ City**.
- Displays **Real Employee Likes & Dislikes** synthesized from 43,000+ AmbitionBox reviews.

### 5. ⚖️ Company vs Company Offer Comparison
- Side-by-side benchmark for job seekers evaluating two offers or target employers.
- Compares CTC, estimated take-home pay delta, culture ratings, total reviews, and top pros/cons.

### 6. 💰 In-Hand / Take-Home Pay Calculator (India New Tax Regime)
- Converts CTC into **actual monthly bank credit** under Budget 2024 / FY 2024-25 & 2025-26 rules:
  - Standard deduction of ₹75,000
  - Slabs: 3-7L (5%), 7-10L (10%), 10-12L (15%), 12-15L (20%), >15L (30%)
  - Section 87A rebate (tax-free CTC up to ~₹7.75 Lakhs)
  - EPF deductions (12% of basic) and Professional Tax (₹2,400/yr)
- Interactive donut chart showing CTC breakdown.

### 7. 📈 15-Year Career Trajectory Simulator
- Simulates how compensation evolves across 0 to 18 years of experience for any role at any company.
- Plots milestone stages: Fresh Graduate, Mid-Level, Senior, and Lead/Principal.

### 8. 🇺🇸 US Onsite H-1B Prevailing Wage Intelligence (US DOL OFLC Data)
- Integrates **100% legal, public government disclosure records** from the **U.S. Department of Labor (DOL)** Office of Foreign Labor Certification (OFLC).
- Tracks over **1,000,000+ certified H-1B visa petitions** across 50 tier-1 Indian IT and multinational technology firms (Infosys: 200k, TCS: 126k, Cognizant: 125k, Google: 42k, etc.).
- Compares **Offshore India CTC** against **US Onsite H-1B Median Wages** with both Direct FX (USD to INR @ 86) and World Bank Purchasing Power Parity (PPP @ 23.5).
- Displays federal prevailing wage tiers (Level I Entry to Level IV Leadership) pursuant to 20 CFR § 656.40.

### 9. 📊 Multi-Source Kaggle Glassdoor India Cross-Validation
- Ingested open research salary benchmarks from Kaggle's Glassdoor India repository (`ruchi798/software-industry-salary-dataset-2022`).
- Matched **2,836 validated individual salary records across 73 target companies**, providing direct offshore triangulation against AmbitionBox figures.
- Live comparison card in the platform displays:
  - Total Glassdoor submission counts per company
  - Empirical P10, P50 (median), and P90 benchmarks
  - Real-time delta between ensemble predictions and Glassdoor medians.

### 10. 🔥 Reddit Unfiltered: The Real Developer Truth Engine (r/developersIndia)
- Directly addresses corporate review sanitization by harvesting and structuring authentic developer discussions from `r/developersIndia` and `r/cscareerquestionsIN`.
- **Culture X-Ray (Corporate PR vs. Reddit Reality):**
  - Side-by-side comparison of polished HR scores vs raw developer sentiment distributions (% Positive, Neutral, Negative, Toxic).
  - Indian tech **Dark Pattern & Red-Flag Radar**: 90-Day Notice Period traps, unbilled bench ultimatums (RMG), silent PIP / stack-ranking quotas (Amazon URA), and delayed/low appraisal stats.
- **Community Leaked CTCs & Compensation Explorer:**
  - Real community-disclosed packages detailing Base, Variable, and ESOPs across IT services, Unicorns, and FAANG/Tier-1 GCCs.
- **Interactive Reddit Offer Evaluator:**
  - Enter proposed CTC, company, and YoE to get an instant, unfiltered community verdict and negotiation risk checklist.

---

## 🛠️ Quickstart & Setup

```bash
# 1. Clone repository and navigate inside
cd salary-predictor

# 2. Install pinned dependencies (including CPU PyTorch, Pytest & PRAW)
pip install -r requirements.txt

# 3. Run automated verification test suite
pytest tests/ -v

# 4. (Optional) Re-train model pipeline & generate company intelligence assets
python train_model.py

# 5. (Optional) Refresh multi-source benchmarks (DOL H-1B, Glassdoor, & Reddit)
python ingest_h1b_dol_data.py
python ingest_glassdoor_data.py
python reddit_harvester.py
python reddit_nlp_extractor.py

# 6. Launch the Streamlit web application
streamlit run app.py
```

---

## 📁 Project Architecture

| File / Directory | Description |
|---|---|
| `app.py` | Multi-tab Streamlit platform with 4 modules: Salary Deep Dive, Offer Compare, Reddit Unfiltered, and AI Copilot |
| `taxonomy.py` | Single source of truth for NLP regex job categorization across 15 Role Families & 5 Seniority Levels |
| `reddit_harvester.py` | Harvester module supporting live Reddit PRAW API crawling and high-fidelity seed corpus fallback |
| `reddit_nlp_extractor.py` | Regex & NLP parser extracting compensation figures, YoE, red flags (90-day notice, bench, PIP), and sentiment |
| `reddit_benchmarks.json` | Pre-computed Reddit scorecards across 22 top tech employers (sentiment, red flags, leaked CTCs, threads) |
| `reddit_threads_cleaned.csv` | Normalized tabular dataset of parsed Reddit developer threads and offer disclosures |
| `reddit_raw_posts.json` | Raw ingested post bodies, scores, permalinks, and top comment trees from r/developersIndia |
| `rag_assistant.py` | RAG module: lazy FAISS loading, review parsing, semantic search, and Gemini/extractive synthesis |
| `faiss_index/` | Local vector index (`index.faiss` + `index.pkl`) storing 33,200+ review embeddings |
| `train_model.py` | Ingests data, applies NLP role normalization, executes 5-fold CV, trains Voting Ensemble |
| `ingest_h1b_dol_data.py` | Ingestion script pulling official US Department of Labor OFLC H-1B LCA public disclosure data |
| `h1b_lca_benchmarks.json` | Pre-computed US DOL H-1B benchmarks for 50 employers (filings, median wage, wage levels) |
| `h1b_summary.csv` | Summary table of top employers by certified H-1B filings and approval rates |
| `ingest_glassdoor_data.py` | Ingestion & normalization script for Kaggle Glassdoor India compensation dataset |
| `glassdoor_benchmarks.json` | Pre-computed Glassdoor benchmarks across 73 employers (sample counts, P10, P50, P90) |
| `glassdoor_salaries_cleaned.csv` | Normalized Glassdoor records mapped to canonical company and role taxonomy |
| `generate_evaluation_plots.py` | Publication-grade evaluation plotting script generating calibration & residual curves |
| `assets/` | High-resolution evaluation charts (`model_evaluation_dashboard.png`, `calibration_plot.png`, etc.) |
| `tests/test_platform.py` | Automated Pytest verification suite covering inference, taxonomy, tax math, and data schemas |
| `.github/workflows/ci.yml` | GitHub Actions CI workflow executing pytest suite on push and pull requests |
| `METHODOLOGY.md` | In-depth technical report: ablation study, 5-fold CV breakdown, segment error analysis, US DOL data integration |
| `evaluation_report.json` | Programmatically exported cross-validation metrics, segment MAEs, and fold scores |
| `salary_data.csv` | Cleaned, deduplicated salary dataset with company ratings, industry, role family, and seniority |
| `company_insights.json` | Pre-aggregated company ratings, review counts, HQ locations, top likes/dislikes |
| `salary_pipeline.pkl` | Trained `sklearn.pipeline.Pipeline` with `VotingRegressor` (RF + HGB) |
| `model_metadata.pkl` | Metadata dictionary: companies, company-job map, role taxonomy, experience caps, test & CV metrics |
| `requirements.txt` | Version-pinned dependencies with CPU-optimized PyTorch wheels for fast container deployment |

---

## 📊 Model Performance

Primary metrics are 5-fold cross-validated (`KFold`, `n_splits=5`, `shuffle=True`, `random_state=42`). A single 15% holdout is reported only as a secondary check; it is not the headline number.

### 5-Fold Cross-Validation & Unconfounded 3-Way Ablation

| Protocol | CV R² | CV MAE (LPA) | CV RMSE (LPA) |
|---|---|---|---|
| **Arm A:** Baseline — raw job titles, single RF | `0.4243 ± 0.1007` | `4.24 ± 0.28` | `6.87 ± 0.61` |
| **Arm B:** NLP taxonomy, single RF *(isolates taxonomy)* | `0.4774 ± 0.0714` | `4.06 ± 0.20` | `6.59 ± 0.49` |
| **Arm C:** NLP taxonomy + voting ensemble *(RF + HGB)* | **`0.4993 ± 0.0620`** | **`3.95 ± 0.18`** | **`6.45 ± 0.45`** |

### Per-Fold Breakdown & Sign Consistency (Arm B vs Arm A)

| Fold | Arm A (Raw RF) | Arm B (Taxonomy RF) | Delta (B − A) | Arm C (Ensemble) |
|---|---|---|---|---|
| Fold 1 | 0.4559 | 0.4971 | **+0.0412** | 0.5003 |
| Fold 2 | 0.5178 | 0.5435 | **+0.0257** | 0.5786 |
| Fold 3 | 0.3043 | 0.4103 | **+0.1060** | 0.4096 |
| Fold 4 | 0.5370 | 0.5578 | **+0.0207** | 0.5533 |
| Fold 5 | 0.3066 | 0.3784 | **+0.0718** | 0.4546 |
| **Mean ± Std** | `0.4243 ± 0.1007` | `0.4774 ± 0.0714` | **+0.0531 (5/5 positive)** | **`0.4993 ± 0.0620`** |

**The dominant effect is variance reduction, not mean lift.** Fold-to-fold standard deviation falls 38% for R² (0.100 → 0.062), 42% for MAE, and 29% for RMSE. Notice especially Fold 3 (+0.1060) and Fold 5 (+0.0718) — the worst-performing slices without taxonomy gained the most. Resolving categorical sparsity across 750+ free-text Indian job titles makes performance *predictable across data slices* — which matters more than a marginal mean gain when serving a long tail of role families and seniority tiers. Adding the `HistGradientBoosting` ensemble further lifts R² to 0.4993 and tightens σ to 0.062.

## 🎯 Interval Calibration & Split Conformal Prediction

Tree-variance P10–P90 bands were audited against out-of-fold actuals:

- Nominal coverage: 80.0%
- Empirical out-of-fold coverage: **71.2%**

The raw tree-variance bands under-cover by ~9 points — they are overconfident and should not be read as calibrated 80% intervals. To provide a rigorous guarantee, we implemented **Split Conformal Prediction on out-of-fold residuals**:

$$\hat{C}(x) = [\hat{y} - q_{\text{val}}, \hat{y} + q_{\text{val}}] \quad \text{where } q_{\text{val}} = \pm 6.01\text{ LPA}$$

- **Conformal Margin ($1-\alpha=0.80$):** $\pm 6.01\text{ LPA}$
- **Empirical Out-of-Fold Coverage:** **80.0%** (finite-sample marginal coverage guarantee)

In the UI, the corridor is explicitly labeled with both the certified **80% Conformal Interval** ($\pm 6.01\text{ LPA}$) and the empirical **model-variance band** (71.2% coverage).

## 🗄️ Training Data vs. Benchmark Data

Only one source trains the model. The rest validate or contextualize it.

| Source | Rows | Role in system |
|---|---|---|
| **AmbitionBox India** | 867 | **Supervised training set** (X, y) |
| **Glassdoor India** | 2,836 | Post-prediction offshore validation card (UI) |
| **US DOL H-1B OFLC** | 1M+ | Standalone US onsite legal-floor reference table |
| **Reddit (22 firms)** | qual. | Qualitative culture X-ray / dark-pattern radar |

H-1B prevailing wages are **legal minimum floors for US-based petitions, not observed wages**, and are never converted, blended, or used as model features. They are surfaced only as an independent offshore-vs-onsite relocation benchmark.

---

## ⚠️ Disclaimers & Fair Use
- AmbitionBox data is self-reported by employees and job candidates, harvested as a mid-2026 snapshot.
- This platform is an educational, non-commercial portfolio project intended for market benchmarking and machine learning research. It is not affiliated with, endorsed by, or sponsored by AmbitionBox or Info Edge India Ltd.
- Compensation figures may vary based on performance bonuses, RSUs/ESOPs, academic tier, specific technology stacks, and negotiation skill. Estimates do not constitute formal tax or legal counsel.
