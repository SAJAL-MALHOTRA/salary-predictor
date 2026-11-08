# 📘 Machine Learning Methodology, Cross-Validation & Technical Ablation Report

> **Project:** India Salary & Career Intelligence Platform  
> **Author:** Sajal Malhotra  
> **Evaluation Date:** November 2026  
> **Status:** Production / Portfolio Research  

---

## 1. Executive Summary & Scientific Purpose

The goal of this project is to build an empirical, data-driven compensation and workplace sentiment intelligence system using self-reported benchmark data across the Indian tech ecosystem. 

Rather than relying on uncalibrated single-point estimates or black-box predictions, this methodology document details:
1. How high-cardinality lexical noise across 750+ job titles was resolved via rule-based canonical taxonomy mapping.
2. Cross-validation performance across 5 randomized folds ($K$-Fold).
3. The empirical results of a target log-transformation experiment.
4. Granular segment-level error analysis demonstrating exactly where and why the model succeeds or struggles.
5. Statistically sound cold-start handling for low-sample employers.

![Model Evaluation & Diagnostic Dashboard](assets/model_evaluation_dashboard.png)

---

## 2. Dataset Composition & Exploratory Statistics

The dataset originates from an educational web-scraping research snapshot harvested from [AmbitionBox](https://www.ambitionbox.com/salaries) in mid-2026.

| Property | Value | Description |
| :--- | :--- | :--- |
| **Total Deduplicated Records ($N$)** | `867` | Unique (Company, Role, Exp, Salary) pairs |
| **Employer Coverage** | `118` | IT services, GCCs, tech startups, and product firms |
| **Unique Scraped Designations** | `758` | Raw job headlines before NLP normalization |
| **Minimum Salary** | `₹0.5 LPA` | Entry-level trainees and non-voice support |
| **Median Salary** | `₹6.7 LPA` | True median of the Indian tech labor sample |
| **Mean Salary** | `₹10.1 LPA` | Arithmetic average |
| **Maximum Salary** | `₹59.2 LPA` | Principal / Senior Leadership in product firms |
| **Target Distribution Skewness** | `+1.954` | Pronounced right-tail skewness |
| **Experience Range** | `0.0 to 25.0 yrs` | Mean: 6.04 yrs, Std: 3.88 yrs, 99th percentile: 19.0 yrs |

---

## 3. Feature Engineering & Taxonomy Ablation

### 3.1 The High-Cardinality Sparsity Problem
With 758 unique job titles across 867 rows, direct one-hot encoding creates extreme categorical sparsity. The model overfits to idiosyncrasies in company-specific nomenclature (e.g., *"Lead Associate - Software QA Automation"* vs. *"SDET-3"*).

### 3.2 Canonical Taxonomy Mapping
We implemented a two-dimensional rule-based regular-expression parser to extract:
1. **15 Canonical Role Families:** *Software & Systems Engineering, Data Science & AI, Data & Analytics, Cloud/DevOps & Security, QA & Testing, Enterprise Solutions (SAP/Salesforce), Product & Project Management, Sales & BD, Marketing, Finance/Banking, HR, Operations, Support/BPO, etc.*
2. **5 Seniority Levels:** *Entry / Junior, Mid-Level, Senior / Lead, Manager / Lead, Executive / Director*.

### 3.3 Ablation Results (Baseline vs. Engineered Pipeline)

| Configuration | Features Used | Estimator | Holdout $R^2$ | Holdout MAE | Holdout RMSE |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Baseline** | Raw Job Title, Company, Avg_Exp | RandomForest (100 trees) | 0.4511 | 4.27 LPA | 6.50 LPA |
| **With Role Taxonomy** | Role Family, Seniority, Company, Industry, Exp | Voting Ensemble (RF 150 + HistGB) | **0.5661** | **3.84 LPA** | **5.78 LPA** |
| **Performance Delta** | — | — | **+25.4%** | **-10.1%** | **-11.1%** |

---

## 4. Rigorous 5-Fold Cross-Validation Evaluation

Single train/test splits (e.g. 85/15) are subject to high sampling variance on sub-1,000 row datasets. To establish defensible generalization bounds, the full dataset was evaluated using a **shuffled 5-Fold Cross-Validation** ($k=5$, random seed 42):

```
Fold 1 (n=174):  R² = 0.5003  |  MAE = 3.89 LPA  |  RMSE = 5.83 LPA
Fold 2 (n=174):  R² = 0.5786  |  MAE = 3.74 LPA  |  RMSE = 6.13 LPA
Fold 3 (n=173):  R² = 0.4096  |  MAE = 4.13 LPA  |  RMSE = 7.13 LPA
Fold 4 (n=173):  R² = 0.5533  |  MAE = 3.82 LPA  |  RMSE = 6.71 LPA
Fold 5 (n=173):  R² = 0.4546  |  MAE = 4.20 LPA  |  RMSE = 6.44 LPA
------------------------------------------------------------------------
CV Summary:      R² = 0.4993 ± 0.0620  |  MAE = 3.95 ± 0.18 LPA  |  RMSE = 6.45 ± 0.45 LPA
```

### Statistical Observations:
- The mean cross-validation MAE is **₹3.95 Lakhs**, with an exceptionally narrow fold-to-fold standard deviation of **$\pm 0.18\text{ LPA}$**.
- Fold 3 exhibited lower $R^2$ (0.4096) due to the presence of an extreme compensation outlier in the validation split (₹59.2 LPA principal architect role), illustrating why RMSE is sensitive to tail variance.

<p align="center">
  <img src="assets/calibration_plot.png" width="48%" alt="Calibration Plot" />
  <img src="assets/residual_distribution.png" width="48%" alt="Residual Distribution" />
</p>
<p align="center"><em>Figure 1: (Left) Actual vs. Predicted Out-of-Fold Calibration with ±20% tolerance corridor. (Right) Gaussian-centered residual distribution demonstrating zero bias.</em></p>

---

## 5. Log-Transformation Target Experiment

Given the positive skewness of the salary distribution ($+1.954$), an experiment was conducted training the ensemble on $\log(1 + y)$ and inverting predictions via $\exp(\hat{y}) - 1$:

| Metric | Linear Target ($y$) | Log-Transformed Target ($\log(1+y)$) | Trade-off Analysis |
| :--- | :---: | :---: | :--- |
| **5-Fold CV Mean MAE** | 3.95 LPA | **3.86 LPA** | Slight overall MAE improvement |
| **0–5 LPA Bracket MAE** | 1.71 LPA | **1.29 LPA** | **-24.6% error reduction** in high-volume baseline tier |
| **5–10 LPA Bracket MAE** | 2.93 LPA | **2.40 LPA** | **-18.1% error reduction** in mid-level IT roles |
| **15–25 LPA Bracket MAE** | 6.02 LPA | 6.77 LPA | +12.5% error penalty |
| **25+ LPA Bracket MAE** | 14.78 LPA | 16.44 LPA | Tail error magnified by exponential back-transformation |

### Architectural Decision:
While log-transformation sharply improves accuracy for junior and mid-level roles ($< ₹10\text{ LPA}$), exponentiation substantially blows out the absolute rupee error on senior compensation ($> ₹25\text{ LPA}$). Because the platform serves both early-career engineers and senior leadership, we deployed the **untransformed linear ensemble** paired with **P10–P90 tree-variance confidence intervals**, allowing honest uncertainty communication for high-salary roles.

---

## 6. Segment-Level Error Transparency (Where the Model Fails)

### 6.1 Error by Role Family

| Role Family | Sample Size ($n$) | Median Actual (LPA) | Out-of-Fold MAE (LPA) | Error Dynamics & Drivers |
| :--- | :---: | :---: | :---: | :--- |
| **Customer Support & BPO** | 70 | 3.4 | **1.27** | Highly standardized industry pay slabs |
| **Marketing & Communications** | 8 | 5.6 | **2.26** | Consistent mid-tier agency pay bands |
| **Sales, BD & Client Relations** | 163 | 4.6 | **2.35** | High sample size, strong experience correlation |
| **General Corporate & Services** | 218 | 5.4 | **3.39** | Broad sample base, stable baseline bands |
| **QA & Quality Engineering** | 39 | 7.2 | **3.93** | Tight band between manual and automation QA |
| **Enterprise Solutions (SAP/ERP)** | 42 | 15.9 | **4.31** | Predictable consulting billing rates |
| **Data & Analytics** | 37 | 13.0 | **4.76** | Consistent progression curve |
| **Software & Systems Engineering** | 124 | 8.6 | **4.95** | Bimodal distribution (service firm vs. tier-1 product) |
| **Finance, Banking & Accounting** | 54 | 6.0 | **5.12** | Divergence between standard accounting and investment roles |
| **Cloud, DevOps & Cybersecurity** | 39 | 12.5 | **6.13** | Rapid skill premium divergence (K8s/SRE vs. sysadmin) |
| **Operations & Supply Chain** | 26 | 6.2 | **6.34** | High variance between field logistics and operations head |
| **Data Science & AI** | 13 | 22.8 | **6.55** | Specialized talent command wide premium bands |
| **Frontend & Mobile Engineering** | 7 | 16.0 | **6.97** | Small sample size ($n=7$), specialized mobile devs |
| **Human Resources** | 10 | 5.9 | **7.23** | Small sample size, executive HRBP outliers |
| **Product & Project Management** | 17 | 18.6 | **11.09** | Extreme dispersion between Scrum Master (₹8L) and Principal PM (₹45L) |

### 6.2 Error by Seniority Level

| Seniority Tier | Sample Size ($n$) | Median Actual (LPA) | Out-of-Fold MAE (LPA) |
| :--- | :---: | :---: | :---: |
| **Entry / Junior** | 13 | 3.1 | **2.12 LPA** |
| **Mid-Level** | 491 | 5.3 | **3.02 LPA** |
| **Manager / Lead** | 198 | 8.6 | **4.58 LPA** |
| **Senior / Lead** | 143 | 13.7 | **5.92 LPA** |
| **Executive / Director** | 22 | 13.2 | **7.62 LPA** |

*Takeaway:* Model error scales almost monotonically with seniority. Entry/Junior roles exhibit tight compensation standardization ($\text{MAE} \approx 2.1\text{ LPA}$), while Director/Executive roles diverge widely due to non-standard negotiation leverage and performance bonuses.

![Segment Error Analysis](assets/segment_error_analysis.png)
*Figure 2: Segment-level Mean Absolute Error (MAE) across 15 Canonical Role Families (left) and 5 Seniority Levels (right).*

---

## 7. Cold-Start Handling Strategy

In the dataset:
- **7 out of 118 employers ($5.9\%$)** have fewer than 3 salary benchmark rows.
- **Problem:** When an employer has low representation, one-hot encoding provides virtually zero unique coefficient signal, risking arbitrary predictions.
- **Solution Implemented in UI & Pipeline:**
  1. `OneHotEncoder(min_frequency=2, handle_unknown="ignore")`: Extremely rare categories are collapsed rather than generating degenerate one-hot columns.
  2. **Contextual Cold-Start Warning:** In `app.py`, if an employer has $< 3$ records on file, an amber notice alerts the user:
     > *"⚠️ Cold-Start Notice: Only X benchmark rows on file for this employer. Estimate relies primarily on the broader domain benchmark and seniority scaling."*
  3. **Hierarchical Shrinkage Intuition:** The model naturally falls back onto the additive sum of `Role_Family`, `Seniority_Level`, and `Industry` coefficients, effectively performing empirical Bayes shrinkage toward the domain prior.

---

## 8. Statistically Sound Uncertainty (P10–P90 Bands)

Rather than outputting a single fragile point estimate, the platform accesses the 150 individual tree estimators inside the Random Forest regressor:

$$\hat{y}_t = T_t(\mathbf{x}), \quad t \in \{1, \dots, 150\}$$

$$\text{P10} = \text{Percentile}(\{\hat{y}_t\}, 10), \quad \text{P90} = \text{Percentile}(\{\hat{y}_t\}, 90), \quad \sigma = \text{std}(\{\hat{y}_t\})$$

- For a **TCS Software Engineer (3y exp)**: $\text{P10} = ₹5.1\text{ LPA}$, $\text{P90} = ₹6.8\text{ LPA}$ ($\sigma = \pm 0.7\text{ LPA}$ — high certainty).
- For an **Uber Engineering Manager (10y exp)**: $\text{P10} = ₹34.2\text{ LPA}$, $\text{P90} = ₹48.5\text{ LPA}$ ($\sigma = \pm 5.2\text{ LPA}$ — properly broad uncertainty band).

---

## 9. Legal Provenance, Fair Use & Disclaimer

1. **Source:** AmbitionBox mid-2026 public data snapshot.
2. **Fair Use / Educational Status:** This project is developed purely as an educational portfolio demonstration of ensemble machine learning, NLP taxonomy design, and RAG systems. It is non-commercial and has no paid tiers or paywalls.
3. **No Affiliation:** This application is completely independent and has no affiliation with AmbitionBox or Info Edge India Ltd.
4. **Data Limitations:** Self-reported figures omit equity grants (RSUs/ESOPs), performance multipliers, and college tier biases. Figures are strategic compasses, not formal tax or legal benchmarks.
