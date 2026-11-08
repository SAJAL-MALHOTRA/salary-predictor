# 🇮🇳 India Salary & Career Intelligence Platform (with RAG AI & Voting Ensemble)

A comprehensive Streamlit web platform for salary estimation, RAG-powered workplace culture analysis, company benchmarking, take-home pay calculations, and career progression modeling in India. Powered by real compensation and review data scraped from **[AmbitionBox](https://www.ambitionbox.com/salaries)** for educational portfolio research.

> 📖 **Deep Dive Technical Report:** Read the complete [Machine Learning Methodology, Cross-Validation & Ablation Report](METHODOLOGY.md) for 5-fold CV breakdowns, segment-level error analysis, and log-transform experiments.

---

## 🚀 Key Modules & Capabilities

### 1. 🎯 Precision Salary Estimation with Voting Ensemble
- **Ensemble Architecture:** `sklearn.pipeline.Pipeline` with `ColumnTransformer` + `VotingRegressor`:
  - **Estimator 1:** `RandomForestRegressor` (150 estimators, max depth 22, min samples split 3).
  - **Estimator 2:** `HistGradientBoostingRegressor` (200 iterations, 31 max leaves).
- **Rigorous Evaluation:**
  - **5-Fold Cross-Validation:** $R^2 = 0.4993 \pm 0.0620$ | $\text{MAE} = 3.95 \pm 0.18\text{ LPA}$ | $\text{RMSE} = 6.45 \pm 0.45\text{ LPA}$
  - **Holdout Test Set (15% split):** $R^2 = 0.5661$ | $\text{MAE} = 3.84\text{ LPA}$ | $\text{RMSE} = 5.78\text{ LPA}$
- Outputs **P10 to P90 confidence intervals** derived from individual tree predictions.
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

---

## 🛠️ Quickstart & Setup

```bash
# 1. Clone repository and navigate inside
cd salary-predictor

# 2. Install pinned dependencies
pip install -r requirements.txt

# 3. Train model pipeline & generate company intelligence assets
python train_model.py

# 4. Launch the Streamlit web application
streamlit run app.py
```

---

## 📁 Project Architecture

| File | Description |
|---|---|
| `app.py` | Full multi-tab Streamlit dashboard with Plotly charts, RAG interface, and tax calculators |
| `rag_assistant.py` | RAG module: lazy FAISS loading, review parsing, semantic search, and Gemini/extractive synthesis |
| `faiss_index/` | Local vector index (`index.faiss` + `index.pkl`) storing 33,200+ review embeddings |
| `train_model.py` | Ingests data, applies NLP role normalization, executes 5-fold CV, trains Voting Ensemble |
| `METHODOLOGY.md` | In-depth technical report: ablation study, 5-fold CV breakdown, segment error analysis |
| `evaluation_report.json` | Programmatically exported cross-validation metrics, segment MAEs, and fold scores |
| `salary_data.csv` | Cleaned, deduplicated salary dataset with company ratings, industry, role family, and seniority |
| `company_insights.json` | Pre-aggregated company ratings, review counts, HQ locations, top likes/dislikes |
| `salary_pipeline.pkl` | Trained `sklearn.pipeline.Pipeline` with `VotingRegressor` (RF + HGB) |
| `model_metadata.pkl` | Metadata dictionary: companies, company-job map, role taxonomy, experience caps, test & CV metrics |
| `requirements.txt` | Version-pinned dependencies with CPU-optimized PyTorch wheels for fast container deployment |

---

## 📊 Rigorous Model Evaluation (AmbitionBox Dataset)

### Holdout Test Split (15%, $n=131$) vs. Baseline

| Metric | Baseline RF (Raw Titles) | Voting Ensemble (RF + HGB) + NLP Taxonomy | Improvement |
|---|---|---|---|
| **R² Score** | `0.4511` | **`0.5661`** | **+25.5%** |
| **MAE** | `4.27 LPA` | **`3.84 LPA`** | **-0.43 LPA** |
| **RMSE** | `6.50 LPA` | **`5.78 LPA`** | **-0.72 LPA** |

### 5-Fold Shuffled Cross-Validation (Full Dataset, $N=867$)

| Fold | R² Score | MAE (LPA) | RMSE (LPA) | Validation Size |
|---|---|---|---|---|
| Fold 1 | 0.5003 | 3.89 | 5.83 | $n=174$ |
| Fold 2 | 0.5786 | 3.74 | 6.13 | $n=174$ |
| Fold 3 | 0.4096 | 4.13 | 7.13 | $n=173$ |
| Fold 4 | 0.5533 | 3.82 | 6.71 | $n=173$ |
| Fold 5 | 0.4546 | 4.20 | 6.44 | $n=173$ |
| **Mean ± Std** | **`0.4993 ± 0.0620`** | **`3.95 ± 0.18 LPA`** | **`6.45 ± 0.45 LPA`** | Full $N=867$ |

---

## ⚠️ Disclaimers & Fair Use
- AmbitionBox data is self-reported by employees and job candidates, harvested as a mid-2026 snapshot.
- This platform is an educational, non-commercial portfolio project intended for market benchmarking and machine learning research. It is not affiliated with, endorsed by, or sponsored by AmbitionBox or Info Edge India Ltd.
- Compensation figures may vary based on performance bonuses, RSUs/ESOPs, academic tier, specific technology stacks, and negotiation skill. Estimates do not constitute formal tax or legal counsel.
