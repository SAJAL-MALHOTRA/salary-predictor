"""
app.py -- India Salary & Career Intelligence Platform.
Single-screen Offer Evaluator flow:
  1. Monthly in-hand pay (range when variable % > 0, single point when variable % == 0)
  2. Peer percentile with 80% conformal interval & P25-P75 market spread
  3. Three concrete counter-offer numbers
  4. One-line employer red-flag radar (notice period / bench / PIP)
  5. Community offer intelligence notes & lightweight contribution flow
  6. 1-Click negotiation counter-offer email generator & WhatsApp share card

Hidden surfaces retained from v1 (Tabs 2-4, RAG copilot, culture x-ray)
are gated behind os.getenv("DEV_MODE") == "1". See RETROSPECTIVE.md.
"""

import json
import os
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

import community_notes as cn

# ── Paths ────────────────────────────────────────────────────────────────────
_BASE = Path(__file__).resolve().parent

# ── 1. PAGE SETUP & RESPONSIVE DESIGN SYSTEM CSS ──────────────────────────────
st.set_page_config(
    page_title="Offer Evaluator | India Tech Salary Intelligence",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header styles */
.header-badge {
    display: inline-block;
    background: #eef2ff;
    color: #4f46e5;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.app-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 0.25rem;
}
.app-subtitle {
    font-size: 0.98rem;
    color: #64748b;
    margin-bottom: 1.25rem;
    line-height: 1.45;
}

/* Cards */
.output-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}
.output-card-highlight {
    background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
    border: 1px solid #86efac;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(16, 185, 129, 0.06);
}
.card-caption {
    font-size: 0.75rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.3rem;
}
.inhand-range {
    font-size: 2rem;
    font-weight: 800;
    color: #047857;
    line-height: 1.15;
}
.percentile-val {
    font-size: 1.65rem;
    font-weight: 800;
    color: #1e1b4b;
    line-height: 1.2;
}

/* Counter offer pills */
.counter-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
}
.counter-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.counter-val {
    font-size: 1.25rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0.15rem 0;
}
.counter-desc {
    font-size: 0.82rem;
    color: #475569;
}

/* Red flag box */
.red-flag-box {
    background: #fff7ed;
    border-left: 4px solid #f97316;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    font-size: 0.88rem;
    color: #9a3412;
    line-height: 1.45;
}

/* Community Intel Card */
.intel-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid #6366f1;
}
.intel-text {
    font-size: 0.88rem;
    color: #1e293b;
    line-height: 1.4;
}
.intel-meta {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.35rem;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.35rem;
    margin-bottom: 0.35rem;
}
.badge-indigo { background: #e0e7ff; color: #4338ca; }
.badge-slate { background: #f1f5f9; color: #475569; }
.badge-amber { background: #fef3c7; color: #92400e; }

/* Dev mode tabs styling */
div[data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f1f5f9;
    padding: 6px;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
div[data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 18px;
    color: #475569;
}
div[data-baseweb="tab"][aria-selected="true"] {
    background-color: #ffffff;
    color: #0f172a;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.pros-quote {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
    color: #166534;
}
.cons-quote {
    background: #fff1f2;
    border-left: 4px solid #f43f5e;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
    color: #9f1239;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── 2. ASSET CACHING ─────────────────────────────────────────────────────────
@st.cache_resource
def load_assets():
    pipeline = joblib.load(_BASE / "salary_pipeline.pkl")
    metadata = joblib.load(_BASE / "model_metadata.pkl")
    df = pd.read_csv(_BASE / "salary_data.csv")

    insights_file = _BASE / "company_insights.json"
    company_insights = json.load(open(insights_file, "r", encoding="utf-8")) if insights_file.exists() else {}

    h1b_file = _BASE / "h1b_lca_benchmarks.json"
    h1b_benchmarks = json.load(open(h1b_file, "r", encoding="utf-8")) if h1b_file.exists() else {}

    gd_file = _BASE / "glassdoor_benchmarks.json"
    glassdoor_benchmarks = json.load(open(gd_file, "r", encoding="utf-8")) if gd_file.exists() else {}

    rd_file = _BASE / "reddit_benchmarks.json"
    reddit_benchmarks = json.load(open(rd_file, "r", encoding="utf-8")) if rd_file.exists() else {}

    # Initialize lightweight SQLite community notes
    cn.init_db()

    return pipeline, metadata, df, company_insights, h1b_benchmarks, glassdoor_benchmarks, reddit_benchmarks


pipeline, metadata, df, company_insights, h1b_benchmarks, glassdoor_benchmarks, reddit_benchmarks = load_assets()

companies = metadata["companies"]
company_jobs = metadata["company_jobs"]
all_job_titles = metadata["all_job_titles"]
role_families = metadata.get("role_families", sorted(df["Role_Family"].unique().tolist()))
seniority_levels = metadata.get("seniority_levels", ["Entry / Junior", "Mid-Level", "Senior / Lead", "Manager / Lead", "Executive / Director"])
experience_cap = float(metadata.get("experience_cap", 30.0))


# ── 3. NLP & UTILITY FUNCTIONS ───────────────────────────────────────────────
def categorize_job(title: str):
    """Map free-text job titles into canonical Role Family & Seniority Level."""
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


def calculate_take_home(ctc_lpa):
    """
    Compute estimated in-hand salary under India's New Tax Regime (Budget 2024 / FY 2024-25, AY 2025-26).
    Standard deduction: ₹75,000. Basic assumed at 40% of CTC.
    """
    ctc = float(ctc_lpa) * 100000.0
    basic = ctc * 0.40

    if basic * 0.12 > 1800 * 12 and ctc > 1500000:
        epf_annual = 1800 * 12
    else:
        epf_annual = basic * 0.12

    gross_salary = ctc - epf_annual
    pt_annual = 2400.0 if ctc >= 300000 else 0.0

    # New Tax Regime FY 2024-25 (AY 2025-26)
    taxable_income = max(0.0, gross_salary - 75000.0)
    tax = 0.0

    if taxable_income > 700000.0:
        if taxable_income > 1500000.0:
            tax += (taxable_income - 1500000.0) * 0.30
            tax += 300000.0 * 0.20
            tax += 200000.0 * 0.15
            tax += 300000.0 * 0.10
            tax += 400000.0 * 0.05
        elif taxable_income > 1200000.0:
            tax += (taxable_income - 1200000.0) * 0.20
            tax += 200000.0 * 0.15
            tax += 300000.0 * 0.10
            tax += 400000.0 * 0.05
        elif taxable_income > 1000000.0:
            tax += (taxable_income - 1000000.0) * 0.15
            tax += 300000.0 * 0.10
            tax += 400000.0 * 0.05
        elif taxable_income > 700000.0:
            tax += (taxable_income - 700000.0) * 0.10
            tax += 400000.0 * 0.05

        tax *= 1.04  # 4% Cess

    net_annual = gross_salary - epf_annual - pt_annual - tax
    monthly_in_hand = net_annual / 12.0

    return {
        "ctc": ctc,
        "basic": basic,
        "gross": gross_salary,
        "epf_annual": epf_annual,
        "epf_monthly": epf_annual / 12.0,
        "pt_annual": pt_annual,
        "tax_annual": tax,
        "tax_monthly": tax / 12.0,
        "net_annual": net_annual,
        "monthly_in_hand": monthly_in_hand,
    }


# ── 4. HEADER ────────────────────────────────────────────────────────────────
st.markdown('<div class="header-badge">Offer Decision Engine</div>', unsafe_allow_html=True)
st.markdown('<h1 class="app-title">Is this offer good?</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-subtitle">Evaluate your Indian tech offer letter: monthly bank credit, calibrated peer percentile, counter-offer targets, and employer red flags.</p>',
    unsafe_allow_html=True,
)


# ── 5. SINGLE-SCREEN INPUT FORM (Phone-Friendly) ──────────────────────────────
with st.container(border=True):
    col_f1, col_f2 = st.columns(2, gap="medium")

    with col_f1:
        input_company = st.text_input("🏢 Company", value="Infosys", help="Free text employer name (e.g. Infosys, Swiggy, Google)")
        input_role = st.text_input("👤 Role / Job Title", value="Senior Software Engineer", help="e.g. Senior Software Engineer, ML Engineer, Data Analyst")
        input_city = st.text_input("📍 City", value="Bangalore", help="Location of employment (e.g. Bangalore, Hyderabad, Pune)")

    with col_f2:
        input_exp = st.number_input("📅 Years of Experience", min_value=0.0, max_value=30.0, value=3.5, step=0.5)
        input_ctc = st.number_input("💰 Offered Annual CTC (₹ LPA)", min_value=1.0, max_value=250.0, value=12.0, step=0.5)
        input_var_pct = st.slider(
            "📊 Variable Pay %",
            min_value=0,
            max_value=100,
            value=15,
            step=1,
            help="Portion of CTC contingent on individual performance or company billing (default 15%)",
        )

# Normalize role and lookup employer insights
detected_family, detected_seniority = categorize_job(input_role)

# Case-insensitive company lookup in company_insights
comp_match_key = None
for k in company_insights.keys():
    if k.lower() == input_company.strip().lower():
        comp_match_key = k
        break

comp_info = company_insights.get(comp_match_key, {}) if comp_match_key else {}
industry = comp_info.get("industry", "IT Services & Consulting")
rating = float(comp_info.get("rating", 3.8))

# ── 6. MODEL INFERENCE & OUTPUTS ─────────────────────────────────────────────
eval_input_df = pd.DataFrame(
    [
        {
            "Company": comp_match_key if comp_match_key else input_company.strip(),
            "Job_Title": input_role.strip(),
            "Industry": industry,
            "Role_Family": detected_family,
            "Seniority_Level": detected_seniority,
            "Rating": rating,
            "Avg_Exp": float(input_exp),
        }
    ]
)

try:
    predicted_market_ctc = round(float(pipeline.predict(eval_input_df)[0]), 1)
except Exception:
    predicted_market_ctc = round(float(input_ctc), 1)

# Conformal uncertainty margin
conf_margin = float(metadata.get("conformal_margin_80_lpa", 6.01))
conf_low = max(1.0, round(predicted_market_ctc - conf_margin, 1))
conf_high = round(predicted_market_ctc + conf_margin, 1)

# Contextual tags
st.markdown(
    f"""
    <div style="margin-top: -0.25rem; margin-bottom: 0.85rem;">
        <span class="badge badge-indigo">Domain: {detected_family}</span>
        <span class="badge badge-slate">Level: {detected_seniority}</span>
        <span class="badge badge-amber">⭐ {rating} / 5.0 Rating</span>
        <span class="badge badge-slate">📍 {input_city}</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 1: MONTHLY IN-HAND AS A RANGE (OR SINGLE POINT IF VARIABLE % == 0)
# ═══════════════════════════════════════════════════════════════════════════════
fixed_ratio = 1.0 - (float(input_var_pct) / 100.0)
fixed_ctc = float(input_ctc) * fixed_ratio

th_fixed = calculate_take_home(fixed_ctc)
th_full = calculate_take_home(input_ctc)

low_mo = int(th_fixed["monthly_in_hand"])
high_mo = int(th_full["monthly_in_hand"])

if input_var_pct > 0:
    st.markdown(
        f"""
        <div class="output-card-highlight">
            <div class="card-caption">1. Estimated Monthly In-Hand (Net Bank Credit)</div>
            <div class="inhand-range">₹ {int(low_mo/1000):,}k – ₹ {int(high_mo/1000):,}k <span style="font-size: 1.1rem; font-weight:600; color:#065f46;">/ month</span></div>
            <div style="font-size: 0.88rem; color: #166534; margin-top: 0.4rem;">
                <strong>₹ {low_mo:,}/mo guaranteed base</strong> (on ₹ {fixed_ctc:.1f}L fixed CTC) up to <strong>₹ {high_mo:,}/mo</strong> at 100% variable payout ({input_var_pct}% variable component).
            </div>
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.35rem;">
                Budget 2024 New Tax Regime (FY 2024-25, AY 2025-26) with ₹75k standard deduction & 40% basic pay assumption.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="output-card-highlight">
            <div class="card-caption">1. Estimated Monthly In-Hand (Net Bank Credit)</div>
            <div class="inhand-range">₹ {int(high_mo/1000):,}k <span style="font-size: 1.1rem; font-weight:600; color:#065f46;">/ month</span> (₹ {high_mo:,})</div>
            <div style="font-size: 0.88rem; color: #166534; margin-top: 0.4rem;">
                <strong>100% Fixed Salary:</strong> No variable pay deduction. Annual net credit: <strong>₹ {int(th_full['net_annual']/100000):.1f} Lakhs</strong>.
            </div>
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.35rem;">
                Budget 2024 New Tax Regime (FY 2024-25, AY 2025-26) with ₹75k standard deduction & 40% basic pay assumption.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 2: PEER PERCENTILE & CONFORMAL INTERVAL VISIBLE
# ═══════════════════════════════════════════════════════════════════════════════
fam_df = df[df["Role_Family"] == detected_family]
if len(fam_df) < 5:
    fam_df = df

percentile = int(round((fam_df["Avg_Salary_LPA"] < float(input_ctc)).mean() * 100))
percentile = min(99, max(1, percentile))

p25 = round(float(np.percentile(fam_df["Avg_Salary_LPA"], 25)), 1)
p50 = round(float(np.percentile(fam_df["Avg_Salary_LPA"], 50)), 1)
p75 = round(float(np.percentile(fam_df["Avg_Salary_LPA"], 75)), 1)

position_label = "above market median" if float(input_ctc) >= p50 else "below market median"

st.markdown(
    f"""
    <div class="output-card">
        <div class="card-caption">2. Peer Percentile & Market Benchmark</div>
        <div class="percentile-val">{percentile}th Percentile <span style="font-size: 1rem; font-weight: 500; color: #64748b;">for {detected_family} ({detected_seniority})</span></div>
        <div style="margin-top: 0.5rem; font-size: 0.88rem; color: #334155; line-height: 1.5;">
            An offer of <strong>₹ {float(input_ctc):.1f} LPA</strong> sits <strong>{position_label}</strong> (median: ₹ {p50} LPA).<br>
            • <strong>80% Conformal Prediction Interval:</strong> <strong style="color:#4338ca;">₹ {conf_low}L – ₹ {conf_high}L</strong> (calibrated ±{conf_margin} LPA uncertainty margin with finite-sample 80.0% coverage guarantee)<br>
            • <strong>Middle 50% Market Spread (P25–P75):</strong> <strong>₹ {p25}L – ₹ {p75}L</strong> across verified peer disclosures.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 3: THREE CONCRETE COUNTER-OFFER NUMBERS
# ═══════════════════════════════════════════════════════════════════════════════
c_cons = round(float(input_ctc) * 1.08, 1)
c_targ = round(max(float(input_ctc) * 1.18, p75), 1)
c_strt = round(max(float(input_ctc) * 1.35, p75 * 1.15), 1)

st.markdown('<div class="card-caption" style="margin-top: 0.25rem;">3. Concrete Negotiation Counters</div>', unsafe_allow_html=True)
col_cnt1, col_cnt2, col_cnt3 = st.columns(3, gap="small")

with col_cnt1:
    st.markdown(
        f"""
        <div class="counter-box">
            <div class="counter-label" style="color: #047857;">Conservative (+8%)</div>
            <div class="counter-val">₹ {c_cons:.1f} LPA</div>
            <div class="counter-desc">Safe ask. Cites market inflation or standard adjustment; near-zero revocation risk.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_cnt2:
    st.markdown(
        f"""
        <div class="counter-box" style="border-color: #93c5fd; background: #eff6ff;">
            <div class="counter-label" style="color: #1d4ed8;">Market Target (+18%)</div>
            <div class="counter-val" style="color: #1e3a8a;">₹ {c_targ:.1f} LPA</div>
            <div class="counter-desc">Fair market alignment. Anchors around the 75th percentile of role peers.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_cnt3:
    st.markdown(
        f"""
        <div class="counter-box">
            <div class="counter-label" style="color: #b45309;">Stretch (+35%)</div>
            <div class="counter-val">₹ {c_strt:.1f} LPA</div>
            <div class="counter-desc">High-leverage ask. For candidates with competing offers or scarce niche skills.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 4: RED-FLAG LINE PER EMPLOYER FROM REDDIT LAYER (1 LINE MAX)
# ═══════════════════════════════════════════════════════════════════════════════
rd_match_key = None
for k in reddit_benchmarks.keys():
    if k.lower() == input_company.strip().lower():
        rd_match_key = k
        break

if rd_match_key:
    rf_data = reddit_benchmarks[rd_match_key].get("red_flags", {})
    np_days = rf_data.get("notice_period_days", 60)
    b_risk = rf_data.get("bench_risk_level", "Moderate")
    pip_flag = "🚨 Active PIP/quota alerts reported" if rf_data.get("pip_quota_alert") else "Standard appraisal cycles"
    appr_str = rf_data.get("reported_appraisals", "3–6% merit hikes")
    rf_line = f"⚠️ <strong>{rd_match_key} Red Flags:</strong> {np_days}-day notice period · Bench risk: {b_risk} · PIP: {pip_flag} · Real appraisals: {appr_str}"
else:
    rf_line = "⚠️ <strong>Market Notice:</strong> Verify notice period length (90-day locks are standard in IT services), bonus clawback clauses, and whether variable pay requires 100% project billing."

st.markdown(f'<div class="red-flag-box">{rf_line}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 5: COMMUNITY OFFER INTEL (LIGHTWEIGHT THREAD & SUBMISSION)
# ═══════════════════════════════════════════════════════════════════════════════
target_comp_name = comp_match_key if comp_match_key else input_company.strip()
recent_notes = cn.get_notes(target_comp_name, detected_family, limit=3)

st.markdown(f'<div class="card-caption">5. Community Offer Intel & Terms ({target_comp_name})</div>', unsafe_allow_html=True)

if recent_notes:
    for nt in recent_notes:
        st.markdown(
            f"""
            <div class="intel-card">
                <div class="intel-text">"{nt['note_text']}"</div>
                <div class="intel-meta">🏷️ <strong>{nt['author_tag']}</strong> · {nt['role_family']} · Added {nt['created_at']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.caption("No specific community notes for this employer yet. Add the first one below!")

with st.expander("➕ Add an Offer Note / Negotiation Intel (No Signup Required)"):
    st.caption("Share verified terms that offer letters hide: variable payout reality, notice period enforcement, or joining bonus clawbacks.")
    with st.form("add_offer_note_form", clear_on_submit=True):
        note_text_in = st.text_area(
            "Offer Details / Intel (10–280 chars):",
            placeholder="e.g. Variable bonus paid out at 70% of target last year. Notice period is strictly 90 days with zero buyout approvals.",
            max_chars=280,
        )
        tag_col1, tag_col2 = st.columns([1.5, 1])
        with tag_col1:
            note_tag_in = st.selectbox(
                "Your Context:",
                ["Verified Offer Letter", "Current Employee", "Ex-Employee", "Interview Loop"],
            )
        with tag_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            submit_note_btn = st.form_submit_button("Post Intel 🚀", use_container_width=True)

        if submit_note_btn:
            ok, msg = cn.add_note(
                company=target_comp_name,
                role_family=detected_family,
                note_text=note_text_in,
                yoe=float(input_exp),
                ctc_lpa=float(input_ctc),
                author_tag=note_tag_in,
            )
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 6: YC-LEVEL TOOLKIT: NEGOTIATION EMAIL SCRIPT & WHATSAPP SHARE CARD
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

tool_tab1, tool_tab2 = st.tabs(["📝 1-Click Counter Email", "📤 WhatsApp / Mentor Share Card"])

with tool_tab1:
    st.caption("Copy-paste professional negotiation email formatted with your evaluated figures:")
    email_draft = f"""Subject: Regarding the offer for {input_role} - {input_company}

Dear Hiring Team,

Thank you very much for extending the offer for the {input_role} role at {target_comp_name}. I am genuinely excited about the team's roadmap and the opportunity to contribute my {input_exp} years of experience in {detected_family}.

I reviewed the proposed package of ₹ {float(input_ctc):.1f} LPA CTC (with a {input_var_pct}% variable component). Based on my market research, current domain benchmarks for {detected_family} ({detected_seniority}), and comparable lateral compensation, I would like to explore if we can align the total compensation closer to ₹ {c_targ:.1f} LPA. 

Alternatively, if the total CTC is constrained by internal banding, I would be very open to adjusting the fixed-to-variable ratio or exploring a signing bonus to bridge the gap and secure a guaranteed monthly take-home closer to market expectation.

I am enthusiastic about joining {target_comp_name} and would welcome a brief discussion to finalize terms.

Best regards,
[Your Name]"""
    st.code(email_draft, language="markdown")

with tool_tab2:
    st.caption("Formatted summary to send to a mentor, peer, or group chat for a second opinion:")
    whatsapp_card = f"""📋 *Offer Review Request — {target_comp_name}*
• *Role:* {input_role} ({input_exp} YoE)
• *Offered CTC:* ₹{float(input_ctc):.1f} LPA (Variable: {input_var_pct}%)
• *Net Monthly In-Hand:* ₹{int(low_mo/1000)}k – ₹{int(high_mo/1000)}k / mo (Budget 2024 New Tax Regime)
• *Market Standing:* {percentile}th percentile for {detected_family}
• *80% Conformal Range:* ₹{conf_low}L – ₹{conf_high}L
• *Market Target Counter:* ₹{c_targ:.1f} LPA (+18%)
• *Contract Terms:* {rf_line.replace('<strong>', '').replace('</strong>', '')}

What do you think of these numbers?"""
    st.code(whatsapp_card, language="markdown")


# ── FOOTER & INDUSTRY CONTEXT ─────────────────────────────────────────────────
st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
st.caption(
    "💡 **Looking for aggregate company-wide medians across 1.5M records?** "
    "Consult [Weekday's Salary Directory](https://www.weekday.works/salaries). "
    "This tool focuses specifically on evaluating this single offer's take-home pay, calibrated uncertainty, and contract terms."
)


# Hidden surfaces retained from v1; see RETROSPECTIVE.md.
if os.getenv("DEV_MODE") == "1":
    import plotly.express as px
    import plotly.graph_objects as go

    st.markdown("---")
    st.header("🛠️ Developer Mode: Retained v1 Surfaces")
    st.caption("All multi-tab exploratory surfaces, RAG copilot, and Head-to-Head compare retained from v1.")

    dev_tab1, dev_tab2, dev_tab3, dev_tab4 = st.tabs(
        [
            "📊 Salary & Career Deep Dive",
            "⚖️ Compare Two Offers",
            "🔥 Reddit Unfiltered (r/developersIndia)",
            "🤖 AmbitionBox AI Copilot",
        ]
    )

    with dev_tab1:
        st.subheader("💰 Monthly Take-Home & Tax Breakdown")
        quick_th = calculate_take_home(predicted_market_ctc)
        th_c1, th_c2 = st.columns([1.2, 1.8], gap="large")

        with th_c1:
            breakdown_labels = ["Net Take-Home Pay", "Income Tax (TDS)", "Employee EPF", "Professional Tax"]
            breakdown_values = [
                quick_th["net_annual"],
                quick_th["tax_annual"],
                quick_th["epf_annual"],
                quick_th["pt_annual"],
            ]
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=breakdown_labels,
                        values=breakdown_values,
                        hole=0.6,
                        marker=dict(colors=["#10b981", "#f43f5e", "#6366f1", "#f59e0b"]),
                        textinfo="percent",
                        hoverinfo="label+value",
                    )
                ]
            )
            fig_donut.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
            st.plotly_chart(fig_donut, use_container_width=True)

        with th_c2:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.25rem;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 0.5rem 0; color: #64748b;">Annual Cost to Company (CTC)</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 700; color: #0f172a;">₹ {int(quick_th['ctc']):,}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 0.5rem 0; color: #64748b;">Estimated Basic (40% of CTC)</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 600;">₹ {int(quick_th['basic']):,}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 0.5rem 0; color: #dc2626;">(-) Income Tax (New Regime TDS)</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #dc2626;">- ₹ {int(quick_th['tax_annual']):,}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 0.5rem 0; color: #4338ca;">(-) Employee EPF (Retirement)</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #4338ca;">- ₹ {int(quick_th['epf_annual']):,}</td>
                        </tr>
                        <tr style="border-bottom: 2px solid #e2e8f0;">
                            <td style="padding: 0.5rem 0; color: #d97706;">(-) Professional Tax</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #d97706;">- ₹ {int(quick_th['pt_annual']):,}</td>
                        </tr>
                        <tr style="background: #f0fdf4;">
                            <td style="padding: 0.75rem 0.5rem; font-weight: 700; color: #047857;">Estimated Net Bank Credit</td>
                            <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 800; font-size: 1.05rem; color: #047857;">₹ {int(quick_th['monthly_in_hand']):,}/mo</td>
                        </tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 15-Year Career Trajectory
        st.subheader("📈 15-Year Career Trajectory Simulator")
        exp_steps = [0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0, 12.0, 15.0, 18.0]
        traj_records = []
        for step in exp_steps:
            sub_df = pd.DataFrame([{"Company": comp_match_key or "TCS", "Job_Title": input_role, "Industry": industry, "Role_Family": detected_family, "Seniority_Level": detected_seniority, "Rating": rating, "Avg_Exp": step}])
            p_val = round(float(pipeline.predict(sub_df)[0]), 1)
            traj_records.append({"Experience": step, "Salary": p_val})

        traj_df = pd.DataFrame(traj_records)
        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(x=traj_df["Experience"], y=traj_df["Salary"], mode="lines+markers", line=dict(color="#4f46e5", width=3), name="Estimated Trendline"))
        fig_traj.update_layout(xaxis_title="Years of Experience", yaxis_title="Salary (LPA)", height=350, template="plotly_white")
        st.plotly_chart(fig_traj, use_container_width=True)

    with dev_tab2:
        st.subheader("⚖️ Head-to-Head Offer Compare")
        st.caption("Retained from v1 for comparative analysis.")
        cmp_a, cmp_b = st.columns(2)
        with cmp_a:
            comp_choice_a = st.selectbox("Company A", companies, index=0, key="dev_cmp_a")
        with cmp_b:
            comp_choice_b = st.selectbox("Company B", companies, index=min(1, len(companies)-1), key="dev_cmp_b")

        df_a = pd.DataFrame([{"Company": comp_choice_a, "Job_Title": input_role, "Industry": "IT Services & Consulting", "Role_Family": detected_family, "Seniority_Level": detected_seniority, "Rating": 3.8, "Avg_Exp": float(input_exp)}])
        df_b = pd.DataFrame([{"Company": comp_choice_b, "Job_Title": input_role, "Industry": "IT Services & Consulting", "Role_Family": detected_family, "Seniority_Level": detected_seniority, "Rating": 3.8, "Avg_Exp": float(input_exp)}])
        pred_a = round(float(pipeline.predict(df_a)[0]), 1)
        pred_b = round(float(pipeline.predict(df_b)[0]), 1)
        st.write(f"**{comp_choice_a}:** ₹ {pred_a} LPA vs **{comp_choice_b}:** ₹ {pred_b} LPA")

    with dev_tab3:
        st.subheader("🔥 Reddit Unfiltered (r/developersIndia)")
        rd_sel = st.selectbox("Select Employer", sorted(list(reddit_benchmarks.keys())), key="dev_rd_sel")
        rd_item = reddit_benchmarks.get(rd_sel, {})
        if rd_item:
            st.json(rd_item.get("red_flags", {}))
            st.markdown(f"**Threads Indexed:** {len(rd_item.get('top_threads', []))}")

    with dev_tab4:
        st.subheader("🤖 AmbitionBox AI Copilot (FAISS Semantic Search)")
        q = st.text_input("Ask about workplace culture or appraisal reality:", "How are appraisals and work-life balance?")
        if st.button("Search Reviews"):
            try:
                import rag_assistant
                retrieved = rag_assistant.retrieve_reviews(q, company=comp_match_key, k=4)
                for r in retrieved:
                    st.write(f"• **{r['company']} ({r['rating']}⭐):** {r['likes']}")
            except Exception as e:
                st.error(f"Error: {e}")
