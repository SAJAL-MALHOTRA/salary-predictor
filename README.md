# 🇮🇳 India Tech Offer Evaluator & Salary Intelligence

[![CI Test Suite](https://github.com/SAJAL-MALHOTRA/salary-predictor/actions/workflows/ci.yml/badge.svg)](https://github.com/SAJAL-MALHOTRA/salary-predictor/actions/workflows/ci.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
![Python 3.11 | 3.12](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Voting%20Ensemble-F7931E?logo=scikit-learn&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

A portfolio project built to evaluate Indian tech job offers during candidate decision windows. Given an employer, job title, years of experience, offered CTC, and variable pay percentage, the tool computes monthly in-hand bank credit under India's New Tax Regime (Budget 2024), places the offer against a cross-validated peer distribution with finite-sample conformal prediction intervals, provides three concrete negotiation counter-figures, surfaces employer contract risks (such as 90-day notice periods and bench policies) from `r/developersIndia`, indexes crowdsourced offer-structure notes, and generates 1-click negotiation counter-emails and WhatsApp share cards.

---

## 1. The Problem

In the Indian technology market, an offer letter quoting "₹15 LPA CTC" rarely translates to ₹1.25 Lakhs deposited into an engineer's bank account. Between statutory Employee Provident Fund deductions (12% of basic), professional tax, New Tax Regime income tax slabs, and variable pay clauses (10% to 25% tied to performance appraisal or project billability), candidates regularly face negative surprises on their first monthly payday. When variable payout is delayed or reduced, guaranteed monthly income drops significantly below expectations.

Compounding this, compensation in India follows an extreme bimodal distribution. Legacy IT service firms (TCS, Infosys, Wipro, Cognizant) anchor early-career engineers at ₹3.5–₹5.0 LPA, while global capability centers (GCCs), high-growth unicorns, and product engineering teams (Google, Uber, Sprinklr, Razorpay) start freshers at ₹20–₹35 LPA. Candidates evaluating lateral moves cannot rely on generic national averages; they need to know where an offer sits across this divide, what monthly cash flow it delivers, and what counter-offer is defensible.

---

## 2. Model Performance

All primary model metrics are 5-fold cross-validated (`KFold`, `n_splits=5`, `shuffle=True`, `random_state=42`) across the training dataset. A single 15% holdout split is reported only as a secondary check; leading with holdout metrics overstates generalization performance on datasets of this size.

| Evaluation Metric | 5-Fold Cross-Validation (Headline) | Secondary Holdout Split (15%, n=131) |
|---|---|---|
| **$R^2$ Score** | **`0.4993 ± 0.0620`** | `0.5661` |
| **Mean Absolute Error (MAE)** | **`3.95 ± 0.18 LPA`** | `3.84 LPA` |
| **Root Mean Squared Error (RMSE)** | **`6.45 ± 0.45 LPA`** | `5.78 LPA` |

> **Methodological Note:** The single holdout $R^2$ of `0.5661` represented a favorable random split. Under 5-fold cross-validation, the model achieves `0.4993 ± 0.0620`. We lead with the cross-validated figure of ~0.50 as the honest measure of out-of-sample predictive capacity.

---

## 3. The 3-Way Ablation

Earlier iterations bundled NLP taxonomy normalization and model ensembling into a single comparison (+14.1% lift), confounding the feature representation effect with the model complexity effect. To isolate attribution cleanly, we evaluated three distinct configurations across the exact same 5 cross-validation folds (identical seed and splits):

| Arm | Configuration | Feature Representation | Estimator | 5-Fold CV $R^2$ | 5-Fold CV MAE | Fold Improvement vs Baseline |
|---|---|---|---|---|---|---|
| **Arm A** | Baseline | Raw job titles (sparse one-hot) | Single Random Forest | `0.4243 ± 0.1007` | `4.24 ± 0.28 LPA` | Base |
| **Arm B** | Taxonomy | Canonical Role Families & Seniority | Single Random Forest | `0.4774 ± 0.0714` | `4.06 ± 0.20 LPA` | **5 / 5 folds improved** (+0.0531 mean lift) |
| **Arm C** | Taxonomy + Ensemble | Canonical Role Families & Seniority | Voting Regressor (RF + HGB) | **`0.4993 ± 0.0620`** | **`3.95 ± 0.18 LPA`** | **5 / 5 folds improved** (+0.0750 mean lift) |

### Key Findings:
1. **Dominant Effect:** The NLP taxonomy accounts for over 70% of total performance improvement and produces a **29% reduction in cross-fold variance** ($\sigma: 0.1007 \to 0.0714$).
2. **Per-Fold Consistency:** Across all 5 folds, Arm B strictly outperformed Arm A (+0.0412, +0.0257, +0.1060, +0.0207, +0.0718).
3. **Ensemble Contribution:** Ensembling (RF + HistGradientBoosting) provided a modest incremental lift (+0.0219 $R^2$) on this 867-row dataset, confirming that reducing categorical sparsity in job titles matters significantly more than adding model capacity.

---

## 4. Interval Calibration

### Tree-Variance Under-Coverage Audit
In initial builds, uncertainty intervals were derived from the empirical standard deviation across individual trees in the Random Forest ($\hat{y} \pm 1.28 \cdot \sigma_{\text{trees}}$ for nominal 80% coverage). An out-of-fold audit revealed severe under-coverage:
- **Nominal Target Coverage:** 80.0%
- **Empirical Out-of-Fold Coverage:** **71.2%**

Tree variance underestimates epistemic uncertainty because trees in a forest are correlated and cannot account for systematic residual bias or unobserved compensation determinants (negotiation leverage, equity cliffs).

### Certified Conformal Intervals
We replaced heuristic tree variance with **split conformal prediction** calibrated on out-of-fold cross-validation residuals:
- **Conformal Margin (80% level):** $q = \pm 6.01\text{ LPA}$
- **Empirical Coverage on Test Data:** **80.0%** (exact finite-sample calibration)
- **Interpretation:** The conformal interval ($\hat{y} \pm 6.01\text{ LPA}$) reflects model prediction uncertainty, whereas the interquartile range (P25–P75) reflects observable market spread. The application displays both distinctly.

---

## 5. Training Data vs. Benchmark Data

To maintain audit integrity, data sources used for model training are kept strictly separate from external context and validation sources:

| Source | Role in System | Records | Outlier & Preprocessing Policy | Notes |
|---|---|---|---|---|
| **AmbitionBox (Scraped Snapshot)** | **Model Training** | 867 company-role aggregated benchmarks across 118 employers | Excluded founder/intern titles, values $< ₹1.5\text{ LPA}$ and $> ₹150\text{ LPA}$, mapped to 15 canonical role families | Primary ground truth used in `train_model.py` pipeline |
| **Kaggle Glassdoor India** | Secondary Validation | 2,836 individual records across 73 employers | Matched canonical employers; extracted P10, P50, P90 | Independent offshore cross-check; not mixed into training rows |
| **U.S. DOL OFLC H-1B Filings** | Legal Wage Floor Benchmark | 1,000,000+ certified petitions across 50 employers | Extracted median USD wages and Levels I–IV prevailing wages | **Not converted to INR or blended with Indian wages.** H-1B figures reflect statutory US immigration floors, not domestic comp |
| **Reddit `r/developersIndia`** | Contract Risk & Sentiment | 22 top tech employers | NLP regex extraction for notice periods, bench policies, PIP alerts | Unmoderated qualitative layer surfacing terms HR scorecards omit |

### Tax Engine Baseline:
The in-hand calculation assumes **40% basic pay** (standard across Indian IT services and consulting agreements). Standard deduction is fixed at ₹75,000 under Budget 2024 / FY 2024-25 (AY 2025-26). Some product engineering firms structure basic pay at 50% of CTC, which slightly increases monthly employee PF deductions.

---

## 6. Positioning vs. Industry Aggregators (The Weekday Contrast)

Industry salary platforms like **Weekday** (YC W21) operate at substantial scale: 412 companies, roughly 15 lakh (1.5 million) salary records, 30-record company thresholds, and inflation adjustments. Their data is generated as the operational exhaust of an active hiring marketplace.

In a direct company-directory comparison ("what does Company X pay on average?"), an independent 867-row model cannot and should not attempt to compete with a 1.5-million-record hiring engine.

**This project does not build a salary directory; it builds an offer decision engine.**

| Dimension | Directory Platforms (e.g. Weekday) | This Project (Offer Evaluator) |
|---|---|---|
| **Primary Question** | "What does this company pay in aggregate?" | "Is *this specific offer letter* good for *me*, right now?" |
| **Core Output** | Median fixed CTC and P25–P75 percentiles | Monthly in-hand range (accounting for variable pay discount), counter targets, red flags |
| **Uncertainty** | Sample spread across candidates | Calibrated 80% conformal interval ($\pm 6.01\text{ LPA}$) around the user's specific parameters |
| **Contract Terms** | Compensation figures only | 90-day notice period traps, bench risks, and PIP quotas from `r/developersIndia` |
| **Use Case** | Passive market browsing | 48-hour active offer evaluation and negotiation preparation |

> *Benchmark data is a commodity; offer evaluation, variable-pay discount modeling, and calibrated uncertainty is the wedge.*

---

## 7. What I Got Wrong

Engineering honest machine learning requires documenting errors caught during review:

1. **Holdout Cherry-Picking:** I initially cited a single-split holdout $R^2$ of `0.5661` as the headline performance metric. It was an optimistic split. I restructured the evaluation to lead with 5-fold cross-validation (`0.4993 ± 0.0620`).
2. **Confounded Ablation:** I claimed a "+14.1% lift from the taxonomy," but the test script had simultaneously upgraded the model from a single Random Forest to a Voting Ensemble. When I decoupled them in a 3-way ablation on identical folds, the taxonomy alone delivered the primary variance reduction (+0.0531 lift, 5/5 folds), while the ensemble added a modest +0.0219.
3. **Uncalibrated Heuristic Intervals:** I assumed the inter-tree standard deviation from Random Forest estimators produced valid 80% confidence bands. An empirical audit showed it only achieved 71.2% coverage. I replaced it with split conformal prediction to certify finite-sample 80.0% coverage.
4. **Log-Target Framing:** While training on $\log(y)$ narrowed percentage relative error on junior brackets, it distorted nominal rupee errors on high-value senior compensation. I retained linear targets evaluated via MAE and certified conformal margins.

---

## 8. What This Project Doesn't Do

- **No Live Hiring Exhaust:** Data relies on an 867-row scraped snapshot across 118 employers; unindexed companies fall back to domain-level and seniority priors.
- **No Equity / ESOP Modeling:** Does not model stock appreciation, 1-year cliff terms, or backloaded vesting schedules.
- **Simplified Tax Scope:** Implements the Budget 2024 New Tax Regime with standard deductions; bespoke flexi-benefits, HRA claims under the Old Regime, or surcharge adjustments for ultra-high earners ($> ₹50\text{ LPA}$) are omitted.
- **No Production Traffic Yet:** Traffic and submission hypotheses are documented with explicit kill/continue criteria in [`RETROSPECTIVE.md`](RETROSPECTIVE.md).

---

## 9. Product & Engineering Architecture

| Module | Purpose | Key Mechanics |
|---|---|---|
| [`app.py`](app.py) | Offer Intelligence Platform | Linear/Stripe design system with 4 core views: Single-Offer Audit, Multi-Offer Decision Matrix, Total Rewards Equity Modeler, and Recruiter War Room |
| [`offer_parser.py`](offer_parser.py) | Offer Letter PDF & Text Parser | Automated extraction of employer, CTC, basic pay, variable pay, joining bonus, notice period, and gratuity via `pdfplumber` and regex |
| [`contract_auditor.py`](contract_auditor.py) | Statutory Contract Trap Auditor | Audits Payment of Gratuity Act 1972 provisions (4.81% basic), Section 89(1) clawbacks, and computes True Guaranteed Cash |
| [`decision_matrix.py`](decision_matrix.py) | Multi-Offer Decision Matrix | Evaluates Offer A vs Offer B vs Current Job with net monthly cash delta, composite risk scores, and notice period buyout breakeven |
| [`equity_engine.py`](equity_engine.py) | Total Rewards & Equity Modeler | Models 4-year vesting schedules (standard 25/25/25/25, Amazon 5/15/40/40), 90-day post-termination exercise traps, and Section 17(2) perquisite tax |
| [`negotiation_war_room.py`](negotiation_war_room.py) | Recruiter Objection War Room | Battle-tested verbal and written rebuttals for the 5 biggest recruiter objections (20% hike caps, variable shifts, 90-day notice, exploding offers) |
| [`report_generator.py`](report_generator.py) | Executive PDF Audit Memo | 1-click publication-grade 2-page Offer Audit Memo generated in-memory via `ReportLab` |
| [`company_tiers.py`](company_tiers.py) | Employer Tier & Negotiation Playbook | Categorizes firms into 4 compensation tiers (Global Tech, Unicorns, Consultancies, IT Services) with empirical P25/Median/P75 bands |
| [`community_notes.py`](community_notes.py) | Crowdsourced Offer Terms Layer | SQLite-backed offer notes engine with solo regex moderation (URL, email, phone, and anti-doxxing guards) |
| [`taxonomy.py`](taxonomy.py) | NLP Job Title Normalization | Maps free-text scraped headlines into 15 Canonical Role Families and 5 Seniority Levels |
| [`train_model.py`](train_model.py) | ML Training & Conformal Calibration | Scikit-learn Pipeline with ColumnTransformer + VotingRegressor (RF + HGB) and split conformal prediction |
| [`tests/test_platform.py`](tests/test_platform.py) | Automated CI Verification | 16 unit tests covering ML inference, Budget 2024 tax engine, PDF parser, equity vesting, decision matrix, war room, and PDF generator |

---

## 10. Setup & Verification

```bash
# 1. Clone repository
git clone https://github.com/SAJAL-MALHOTRA/salary-predictor.git
cd salary-predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run automated verification suite (16 tests)
pytest tests/ -v

# 4. Launch Offer Intelligence application
streamlit run app.py

# 5. (Optional) Run with developer surfaces enabled (Tabs 2-4, RAG copilot)
DEV_MODE=1 streamlit run app.py
```

---

## 11. Key References & Project Links

- **Technical Report & Ablation Details:** [`METHODOLOGY.md`](METHODOLOGY.md)
- **Six-Week Launch Retrospective & Metrics:** [`RETROSPECTIVE.md`](RETROSPECTIVE.md)
- **Full Model Metrics & Calibration Artifact:** [`evaluation_report.json`](evaluation_report.json)
- **High-Resolution Evaluation Plots:** [`assets/`](assets/)
- **Aggregate Directory Reference:** [Weekday India Salaries](https://www.weekday.works/salaries)
