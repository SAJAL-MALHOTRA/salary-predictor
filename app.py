"""
app.py -- India Salary & Career Intelligence Platform.
YC-Caliber Offer Decision Engine & Contract Risk Platform.

Features:
  1. YC-level SEO Meta tags (OpenGraph, Twitter Cards, JSON-LD Structured Data)
  2. 1-Click Instant Preset Pills (Infosys, Google, Swiggy, TCS)
  3. Interactive In-Hand Monthly Take-Home (0%, 50%, 100% Variable Scenarios + Itemized Pay Slip)
  4. Visual Paper CTC vs True Guaranteed Cash Gap Meter
  5. Visual Horizontal Percentile Distribution Spectrum Bar (P25, Median, P75)
  6. Split Conformal Uncertainty Interval (calibrated +/- 6.01 LPA)
  7. Tier-Specific Negotiation Matrix & Concrete Counters
  8. r/developersIndia Contract Red-Flag Radar
  9. SQLite Crowdsourced Offer Notes with Solo Moderation
  10. 3-Template Negotiation Email Suite & WhatsApp Review Share Card
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
import contract_auditor as ca
import company_tiers as ct
from taxonomy import categorize_job

# ── Paths ────────────────────────────────────────────────────────────────────
_BASE = Path(__file__).resolve().parent

# ── 1. PAGE SETUP & YC-LEVEL DESIGN SYSTEM CSS ───────────────────────────────
st.set_page_config(
    page_title="India Tech Offer Evaluator | Is Your Offer Good?",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# SEO Meta Tags & OpenGraph injection
st.markdown(
    """
    <head>
        <meta name="description" content="Evaluate Indian tech job offers in seconds. Calculate monthly bank credit under Budget 2024 New Tax Regime, detect gratuity and clawback contract traps, and benchmark calibrated peer percentiles across 118 verified employers." />
        <meta name="keywords" content="salary predictor India, tech salary India, in-hand salary calculator, CTC to in hand India, 90 day notice period, TCS salary, Infosys salary, Google salary India, offer negotiation email" />
        <meta property="og:title" content="India Tech Offer Evaluator | Is Your Offer Good?" />
        <meta property="og:description" content="Calculate real monthly bank credit, detect contract traps, and get calibrated peer percentiles before signing." />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="India Tech Offer Evaluator" />
        <meta name="twitter:description" content="Calculate real monthly bank credit, detect contract traps, and get calibrated peer percentiles." />
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "WebApplication",
          "name": "India Tech Offer Evaluator",
          "description": "Compensation decision engine and contract auditor for Indian tech professionals",
          "applicationCategory": "FinanceApplication",
          "operatingSystem": "All"
        }
        </script>
    </head>
    """,
    unsafe_allow_html=True,
)

# Premium FinTech CSS Design System
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0f172a;
}

/* App Header & Badges */
.hero-badge-strip {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 0.75rem;
}
.hero-pill {
    background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
    color: #4338ca;
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.3rem 0.85rem;
    border-radius: 9999px;
    border: 1px solid #c7d2fe;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.hero-pill-live {
    background: #ecfdf5;
    color: #065f46;
    border-color: #a7f3d0;
}
.app-headline {
    font-size: 2.4rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.04em;
    line-height: 1.15;
    margin-bottom: 0.35rem;
}
.app-subheadline {
    font-size: 1.05rem;
    color: #475569;
    line-height: 1.5;
    margin-bottom: 1.25rem;
}

/* Trust Bar */
.trust-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 0.6rem 0;
    margin-bottom: 1rem;
    font-size: 0.8rem;
    color: #64748b;
    border-bottom: 1px solid #f1f5f9;
}
.trust-item {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-weight: 600;
}

/* Cards */
.card-shell {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.25rem 1.45rem;
    margin-bottom: 1.15rem;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
}
.card-shell-emerald {
    background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
    border: 1px solid #86efac;
    border-radius: 16px;
    padding: 1.25rem 1.45rem;
    margin-bottom: 1.15rem;
    box-shadow: 0 6px 20px -2px rgba(16, 185, 129, 0.08);
}
.card-label {
    font-size: 0.76rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
}
.metric-hero {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.25rem;
    font-weight: 800;
    color: #047857;
    line-height: 1.15;
}
.metric-indigo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.85rem;
    font-weight: 800;
    color: #1e1b4b;
    line-height: 1.2;
}

/* Scenario Micro-Cards */
.scenario-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 0.85rem;
}
.scenario-item {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.85rem 0.95rem;
    text-align: center;
}
.scenario-tag {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #64748b;
    letter-spacing: 0.04em;
}
.scenario-amount {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 800;
    margin: 0.25rem 0;
}

/* Trap Meter Progress Bar */
.trap-meter-shell {
    background: #fee2e2;
    border-radius: 9999px;
    height: 14px;
    overflow: hidden;
    position: relative;
    margin: 0.6rem 0;
}
.trap-meter-fill {
    background: linear-gradient(90deg, #10b981 0%, #059669 100%);
    height: 100%;
    border-radius: 9999px;
    transition: width 0.4s ease;
}

/* Percentile Spectrum Bar */
.spectrum-bar-shell {
    background: #e2e8f0;
    border-radius: 9999px;
    height: 10px;
    position: relative;
    margin: 1.2rem 0 0.8rem 0;
}
.spectrum-fill {
    background: linear-gradient(90deg, #6366f1 0%, #4338ca 100%);
    height: 100%;
    border-radius: 9999px;
}
.spectrum-marker {
    position: absolute;
    top: -24px;
    transform: translateX(-50%);
    background: #1e1b4b;
    color: #ffffff;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 0.15rem 0.45rem;
    border-radius: 6px;
    white-space: nowrap;
}

/* Counter Box */
.counter-card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 0.95rem 1.1rem;
    height: 100%;
}
.counter-tag {
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.counter-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.35rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0.2rem 0;
}

/* Red Flag Notice */
.alert-notice {
    background: #fff7ed;
    border-left: 4px solid #f97316;
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    font-size: 0.88rem;
    color: #9a3412;
    line-height: 1.5;
    margin: 0.6rem 0 1rem 0;
}

/* Intel Card */
.intel-bubble {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #6366f1;
    border-radius: 12px;
    padding: 0.9rem 1.15rem;
    margin-bottom: 0.65rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 0.22rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.76rem;
    font-weight: 600;
    margin-right: 0.35rem;
    margin-bottom: 0.35rem;
}
.badge-indigo { background: #e0e7ff; color: #4338ca; }
.badge-slate { background: #f1f5f9; color: #475569; }
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-emerald { background: #d1fae5; color: #065f46; }

/* Dev Mode Tabs */
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

    cn.init_db()

    return pipeline, metadata, df, company_insights, h1b_benchmarks, glassdoor_benchmarks, reddit_benchmarks


pipeline, metadata, df, company_insights, h1b_benchmarks, glassdoor_benchmarks, reddit_benchmarks = load_assets()

companies = metadata["companies"]
company_jobs = metadata["company_jobs"]
all_job_titles = metadata["all_job_titles"]
role_families = metadata.get("role_families", sorted(df["Role_Family"].unique().tolist()))
seniority_levels = metadata.get("seniority_levels", ["Entry / Junior", "Mid-Level", "Senior / Lead", "Manager / Lead", "Executive / Director"])
experience_cap = float(metadata.get("experience_cap", 30.0))


# ── 3. TAX ENGINE & UTILITY FUNCTIONS ─────────────────────────────────────────
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


# ── 4. HERO HEADER ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-badge-strip">
        <span class="hero-pill">⚡ India Tech Offer Intelligence</span>
        <span class="hero-pill hero-pill-live">● Budget 2024 Engine Active</span>
    </div>
    <h1 class="app-headline">Is your tech offer actually good?</h1>
    <p class="app-subheadline">
        Evaluate quoted CTC against actual monthly bank credit, detect statutory contract traps,
        benchmark peer percentiles by employer tier, and generate tactical negotiation leverage.
    </p>
    <div class="trust-bar">
        <span class="trust-item">🔒 Zero Signup Required</span>
        <span class="trust-item">🏢 118 Verified Employers</span>
        <span class="trust-item">⚖️ Payment of Gratuity Act 1972 Audit</span>
        <span class="trust-item">🎯 Split Conformal ±6.0L Uncertainty</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── 5. QUICK-FILL PRESET PILLS ────────────────────────────────────────────────
# Initialize session state defaults if absent
if "cfg_company" not in st.session_state:
    st.session_state.cfg_company = "Infosys"
if "cfg_role" not in st.session_state:
    st.session_state.cfg_role = "Senior Software Engineer"
if "cfg_exp" not in st.session_state:
    st.session_state.cfg_exp = 3.5
if "cfg_ctc" not in st.session_state:
    st.session_state.cfg_ctc = 12.0
if "cfg_var" not in st.session_state:
    st.session_state.cfg_var = 15
if "cfg_city" not in st.session_state:
    st.session_state.cfg_city = "Bangalore"

st.markdown('<div class="card-label">⚡ Quick-Fill Example Offers (Click to Test):</div>', unsafe_allow_html=True)
pill_c1, pill_c2, pill_c3, pill_c4 = st.columns(4)

if pill_c1.button("🏢 Infosys · 3.5y (₹12L)", use_container_width=True):
    st.session_state.cfg_company = "Infosys"
    st.session_state.cfg_role = "Senior Software Engineer"
    st.session_state.cfg_exp = 3.5
    st.session_state.cfg_ctc = 12.0
    st.session_state.cfg_var = 15
    st.session_state.cfg_city = "Bangalore"
    st.rerun()

if pill_c2.button("🦄 Swiggy · 4y (₹24L)", use_container_width=True):
    st.session_state.cfg_company = "Swiggy"
    st.session_state.cfg_role = "SDE 2"
    st.session_state.cfg_exp = 4.0
    st.session_state.cfg_ctc = 24.0
    st.session_state.cfg_var = 18
    st.session_state.cfg_city = "Bangalore"
    st.rerun()

if pill_c3.button("🌐 Google · 3y (₹35L)", use_container_width=True):
    st.session_state.cfg_company = "Google"
    st.session_state.cfg_role = "Software Engineer 3"
    st.session_state.cfg_exp = 3.0
    st.session_state.cfg_ctc = 35.0
    st.session_state.cfg_var = 15
    st.session_state.cfg_city = "Hyderabad"
    st.rerun()

if pill_c4.button("⚙️ TCS · 1.5y (₹4.5L)", use_container_width=True):
    st.session_state.cfg_company = "TCS"
    st.session_state.cfg_role = "Assistant System Engineer"
    st.session_state.cfg_exp = 1.5
    st.session_state.cfg_ctc = 4.5
    st.session_state.cfg_var = 10
    st.session_state.cfg_city = "Pune"
    st.rerun()

st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)


# ── 6. SINGLE-SCREEN INPUT FORM ───────────────────────────────────────────────
with st.container(border=True):
    col_f1, col_f2 = st.columns(2, gap="medium")

    with col_f1:
        input_company = st.text_input(
            "🏢 Company Name",
            value=st.session_state.cfg_company,
            help="Free text employer name (e.g. Infosys, Swiggy, Google, TCS, Razorpay)",
        )
        input_role = st.text_input(
            "👤 Role / Job Title",
            value=st.session_state.cfg_role,
            help="e.g. Senior Software Engineer, ML Engineer, Data Analyst",
        )
        input_city = st.text_input(
            "📍 Employment City",
            value=st.session_state.cfg_city,
            help="e.g. Bangalore, Hyderabad, Pune, Gurgaon",
        )

    with col_f2:
        input_exp = st.number_input(
            "📅 Total Experience (Years)",
            min_value=0.0,
            max_value=30.0,
            value=float(st.session_state.cfg_exp),
            step=0.5,
        )
        input_ctc = st.number_input(
            "💰 Offered Annual CTC (₹ LPA)",
            min_value=1.0,
            max_value=250.0,
            value=float(st.session_state.cfg_ctc),
            step=0.5,
        )
        input_var_pct = st.slider(
            "📊 Variable Pay %",
            min_value=0,
            max_value=100,
            value=int(st.session_state.cfg_var),
            step=1,
            help="Portion of CTC contingent on individual appraisal or company billability (default 15%)",
        )

# Normalize role & classify employer tier
detected_family, detected_seniority = categorize_job(input_role)
tier_info = ct.classify_employer_tier(input_company)

# Case-insensitive company lookup in company_insights
comp_match_key = None
for k in company_insights.keys():
    if k.lower() == input_company.strip().lower():
        comp_match_key = k
        break

comp_info = company_insights.get(comp_match_key, {}) if comp_match_key else {}
industry = comp_info.get("industry", "IT Services & Consulting")
rating = float(comp_info.get("rating", 3.8))

# Conformal uncertainty margin
conf_margin = float(metadata.get("conformal_margin_80_lpa", 6.01))
conf_low = max(1.0, round(float(input_ctc) - conf_margin, 1))
conf_high = round(float(input_ctc) + conf_margin, 1)

# Contextual tags strip
st.markdown(
    f"""
    <div style="margin-top: -0.25rem; margin-bottom: 1rem;">
        <span class="badge {tier_info['badge_color']}">🏷️ {tier_info['tier_badge']}</span>
        <span class="badge badge-indigo">💻 {detected_family}</span>
        <span class="badge badge-slate">🎖️ {detected_seniority}</span>
        <span class="badge badge-amber">⭐ {rating} / 5.0 Rating</span>
        <span class="badge badge-slate">📍 {input_city}</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 1: MONTHLY IN-HAND CASH FLOW (0%, 50%, 100% SCENARIOS)
# ═══════════════════════════════════════════════════════════════════════════════
fixed_ratio = 1.0 - (float(input_var_pct) / 100.0)
fixed_ctc = float(input_ctc) * fixed_ratio

th_0 = calculate_take_home(fixed_ctc)
th_50 = calculate_take_home(fixed_ctc + (float(input_ctc) * float(input_var_pct) / 200.0))
th_100 = calculate_take_home(input_ctc)

low_mo = int(th_0["monthly_in_hand"])
mid_mo = int(th_50["monthly_in_hand"])
high_mo = int(th_100["monthly_in_hand"])

if input_var_pct > 0:
    st.markdown(
        f"""
        <div class="card-shell-emerald">
            <div class="card-label">1. Estimated Monthly In-Hand (Net Bank Credit)</div>
            <div class="metric-hero">₹ {int(low_mo/1000):,}k – ₹ {int(high_mo/1000):,}k <span style="font-size: 1.15rem; font-weight:600; color:#065f46;">/ month</span></div>
            <div style="font-size: 0.88rem; color: #166534; margin-top: 0.35rem;">
                <strong>₹ {low_mo:,}/mo guaranteed floor</strong> (on ₹ {fixed_ctc:.1f}L fixed CTC) up to <strong>₹ {high_mo:,}/mo</strong> at 100% variable payout.
            </div>
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.35rem;">
                Budget 2024 New Tax Regime (FY 2024-25, AY 2025-26) · ₹75k standard deduction · 40% basic pay assumption.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3-Tier Scenario Cards
    st.markdown(
        f"""
        <div class="scenario-grid">
            <div class="scenario-item" style="border-left: 3px solid #dc2626;">
                <div class="scenario-tag" style="color: #dc2626;">0% Variable (Floor)</div>
                <div class="scenario-amount" style="color: #dc2626;">₹ {int(low_mo):,}</div>
                <div class="scenario-tag">Guaranteed ₹ {fixed_ctc:.1f}L Fixed</div>
            </div>
            <div class="scenario-item" style="border-left: 3px solid #4f46e5; background: #f8fafc;">
                <div class="scenario-tag" style="color: #4f46e5;">50% Variable (Realistic)</div>
                <div class="scenario-amount" style="color: #1e1b4b;">₹ {int(mid_mo):,}</div>
                <div class="scenario-tag">Industry Avg Payout</div>
            </div>
            <div class="scenario-item" style="border-left: 3px solid #10b981; background: #f0fdf4;">
                <div class="scenario-tag" style="color: #047857;">100% Variable (Target)</div>
                <div class="scenario-amount" style="color: #047857;">₹ {int(high_mo):,}</div>
                <div class="scenario-tag">Full ₹ {float(input_ctc):.1f}L CTC</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="card-shell-emerald">
            <div class="card-label">1. Estimated Monthly In-Hand (Net Bank Credit)</div>
            <div class="metric-hero">₹ {int(high_mo/1000):,}k <span style="font-size: 1.15rem; font-weight:600; color:#065f46;">/ month</span> (₹ {high_mo:,})</div>
            <div style="font-size: 0.88rem; color: #166534; margin-top: 0.35rem;">
                <strong>100% Fixed Salary:</strong> No variable pay deduction. Annual net credit: <strong>₹ {int(th_100['net_annual']/100000):.1f} Lakhs</strong>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Itemized Pay Slip Expander
with st.expander("🧾 View Itemized Monthly Pay Slip Breakdown"):
    st.markdown(
        f"""
        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 0.45rem 0; color: #64748b;">Annual Cost to Company (CTC)</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 700;">₹ {int(th_100['ctc']):,}</td>
                <td style="padding: 0.45rem 0; text-align: right; color: #64748b;">₹ {int(th_100['ctc']/12):,}/mo</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 0.45rem 0; color: #64748b;">Basic Salary (40% of CTC)</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 600;">₹ {int(th_100['basic']):,}</td>
                <td style="padding: 0.45rem 0; text-align: right; color: #64748b;">₹ {int(th_100['basic']/12):,}/mo</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 0.45rem 0; color: #dc2626;">(-) Income Tax (New Regime TDS)</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 600; color: #dc2626;">- ₹ {int(th_100['tax_annual']):,}</td>
                <td style="padding: 0.45rem 0; text-align: right; color: #dc2626;">- ₹ {int(th_100['tax_monthly']):,}/mo</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 0.45rem 0; color: #4338ca;">(-) Employee EPF (Retirement)</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 600; color: #4338ca;">- ₹ {int(th_100['epf_annual']):,}</td>
                <td style="padding: 0.45rem 0; text-align: right; color: #4338ca;">- ₹ {int(th_100['epf_monthly']):,}/mo</td>
            </tr>
            <tr style="border-bottom: 2px solid #e2e8f0;">
                <td style="padding: 0.45rem 0; color: #d97706;">(-) Professional Tax</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 600; color: #d97706;">- ₹ {int(th_100['pt_annual']):,}</td>
                <td style="padding: 0.45rem 0; text-align: right; color: #d97706;">- ₹ {int(th_100['pt_annual']/12):,}/mo</td>
            </tr>
            <tr style="background: #f0fdf4;">
                <td style="padding: 0.65rem 0.5rem; font-weight: 700; color: #047857;">Estimated Net Bank Credit</td>
                <td style="padding: 0.65rem 0.5rem; text-align: right; font-weight: 800; font-size: 1.05rem; color: #047857;">₹ {int(th_100['net_annual']):,}</td>
                <td style="padding: 0.65rem 0.5rem; text-align: right; font-weight: 800; font-size: 1.05rem; color: #047857;">₹ {int(th_100['monthly_in_hand']):,}/mo</td>
            </tr>
        </table>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 2: OFFER TRAP DETECTOR & PAPER CTC REALITY CHECK
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

with st.expander("🛡️ Offer Trap Detector & Paper CTC Reality Check", expanded=True):
    st.caption("Quantify hidden deductions: Payment of Gratuity Act 1972 phantom provisions, annual variable locks, and Section 89(1) clawbacks.")

    trap_col1, trap_col2 = st.columns(2)
    with trap_col1:
        gratuity_inc = st.checkbox("Gratuity included in CTC sheet?", value=True, help="Standard in >80% of Indian IT offers (4.81% of basic salary)")
        var_freq = st.radio("Variable Pay Payout Frequency", ["Annual Payout (High Forfeiture Risk)", "Quarterly Payout"], horizontal=True)

    with trap_col2:
        jb_amt = st.number_input("Joining / Sign-on Bonus (₹ LPA, optional)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
        exp_tenure = st.slider("Expected Tenure at this Company (Years)", min_value=1.0, max_value=6.0, value=2.0, step=0.5)

    # Match notice period for audit
    rd_match_key = None
    for k in reddit_benchmarks.keys():
        if k.lower() == input_company.strip().lower():
            rd_match_key = k
            break
    rf_data_temp = reddit_benchmarks[rd_match_key].get("red_flags", {}) if rd_match_key else {}
    detected_np = rf_data_temp.get("notice_period_days", tier_info["typical_notice_days"])

    contract_audit = ca.audit_offer_contract(
        ctc_lpa=input_ctc,
        variable_pct=input_var_pct,
        gratuity_included=gratuity_inc,
        joining_bonus_lpa=jb_amt,
        clawback_months=12 if jb_amt > 0 else 0,
        notice_period_days=detected_np,
        variable_freq="Quarterly" if "Quarterly" in var_freq else "Annual",
        expected_tenure_years=exp_tenure,
    )

    # Visual Paper CTC Gap Meter
    guaranteed_pct = max(0, min(100, int(100 - contract_audit["paper_inflation_gap_pct"])))
    st.markdown(
        f"""
        <div style="margin-top: 0.5rem; margin-bottom: 0.3rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700;">
                <span style="color: #047857;">Guaranteed Cash: ₹ {contract_audit['guaranteed_year1_cash_lpa']} LPA ({guaranteed_pct}%)</span>
                <span style="color: #c2410c;">Paper CTC Gap: {contract_audit['paper_inflation_gap_pct']}% at-risk</span>
            </div>
            <div class="trap-meter-shell">
                <div class="trap-meter-fill" style="width: {guaranteed_pct}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t_res1, t_res2 = st.columns(2)
    with t_res1:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #fed7aa; border-radius: 10px; padding: 0.85rem 1rem;">
                <div class="scenario-tag" style="color: #9a3412;">True Guaranteed Year-1 Cash</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 800; color: #c2410c;">₹ {contract_audit['guaranteed_year1_cash_lpa']} LPA</div>
                <div class="scenario-tag">Fixed CTC minus phantom gratuity provisions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t_res2:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #fed7aa; border-radius: 10px; padding: 0.85rem 1rem;">
                <div class="scenario-tag" style="color: #9a3412;">Paper CTC Inflation Gap</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 800; color: #c2410c;">{contract_audit['paper_inflation_gap_pct']}% Gap</div>
                <div class="scenario-tag">₹ {int(contract_audit['paper_inflation_gap_rupees']):,} uncollected if variable drops or early exit</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Diagnostic flag warnings
    st.markdown(f'<div class="alert-notice">{contract_audit["gratuity_flag"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alert-notice">{contract_audit["variable_timing_flag"]}</div>', unsafe_allow_html=True)
    if jb_amt > 0:
        st.markdown(f'<div class="alert-notice">{contract_audit["clawback_flag"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alert-notice">{contract_audit["notice_flag"]}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 3: PEER PERCENTILE & TIER MARKET BENCHMARK
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

tier_spread = ct.get_tier_market_spread(tier_info["tier_num"], detected_seniority)
p25 = tier_spread["p25"]
p50 = tier_spread["median"]
p75 = tier_spread["p75"]

if float(input_ctc) <= p25:
    percentile = int(max(5, round(25 * (float(input_ctc) / p25))))
elif float(input_ctc) <= p50:
    percentile = int(round(25 + 25 * ((float(input_ctc) - p25) / (p50 - p25))))
elif float(input_ctc) <= p75:
    percentile = int(round(50 + 25 * ((float(input_ctc) - p50) / (p75 - p50))))
else:
    percentile = int(min(98, round(75 + 20 * ((float(input_ctc) - p75) / max(10.0, p75 * 0.5)))))

position_label = "above tier median" if float(input_ctc) >= p50 else "below tier median"

st.markdown(
    f"""
    <div class="card-shell">
        <div class="card-label">3. Peer Standing & Tier Market Benchmark</div>
        <div class="metric-indigo">{percentile}th Percentile <span style="font-size: 1.05rem; font-weight: 500; color: #64748b;">for {detected_family} ({detected_seniority} · {tier_info['tier_badge']})</span></div>
        <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #334155; line-height: 1.55;">
            An offer of <strong>₹ {float(input_ctc):.1f} LPA</strong> sits <strong>{position_label}</strong> (tier median: ₹ {p50} LPA).<br>
            • <strong>80% Conformal Uncertainty Interval:</strong> <strong style="color:#4338ca;">₹ {conf_low}L – ₹ {conf_high}L</strong> (calibrated ±{conf_margin} LPA uncertainty margin with finite-sample 80.0% coverage guarantee)<br>
            • <strong>Middle 50% Tier Market Spread (P25–P75):</strong> <strong>₹ {p25}L – ₹ {p75}L</strong> for {tier_info['tier_name']}.
        </div>
        <!-- Visual Spectrum Bar -->
        <div class="spectrum-bar-shell">
            <div class="spectrum-marker" style="left: {percentile}%;">You ({percentile}%)</div>
            <div class="spectrum-fill" style="width: {percentile}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #64748b; font-weight: 700;">
            <span>P25: ₹{p25}L</span>
            <span>Median: ₹{p50}L</span>
            <span>P75: ₹{p75}L</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 4: THREE CONCRETE COUNTER-OFFER NUMBERS & PLAYBOOK
# ═══════════════════════════════════════════════════════════════════════════════
c_cons = round(float(input_ctc) * 1.08, 1)
c_targ = round(max(float(input_ctc) * 1.18, p75), 1)
c_strt = round(max(float(input_ctc) * 1.35, p75 * 1.15), 1)

st.markdown('<div class="card-label">4. Concrete Negotiation Counters & Strategy</div>', unsafe_allow_html=True)
col_cnt1, col_cnt2, col_cnt3 = st.columns(3, gap="small")

with col_cnt1:
    st.markdown(
        f"""
        <div class="counter-card">
            <div class="counter-tag" style="color: #047857;">Conservative (+8%)</div>
            <div class="counter-number">₹ {c_cons:.1f} LPA</div>
            <div class="counter-desc">Safe ask citing market inflation or standard adjustment; near-zero revocation risk.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_cnt2:
    st.markdown(
        f"""
        <div class="counter-card" style="border-color: #93c5fd; background: #eff6ff;">
            <div class="counter-tag" style="color: #1d4ed8;">Market Target (+18%)</div>
            <div class="counter-number" style="color: #1e3a8a;">₹ {c_targ:.1f} LPA</div>
            <div class="counter-desc">Fair market alignment. Anchors around the 75th percentile of role peers.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_cnt3:
    st.markdown(
        f"""
        <div class="counter-card">
            <div class="counter-tag" style="color: #b45309;">Stretch (+35%)</div>
            <div class="counter-number">₹ {c_strt:.1f} LPA</div>
            <div class="counter-desc">High-leverage ask for candidates with competing offers or scarce niche skills.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 12px; padding: 0.95rem 1.15rem; margin-top: 0.75rem; font-size: 0.86rem; color: #334155; line-height: 1.5;">
        <div style="font-weight: 700; color: #0f172a; margin-bottom: 0.25rem;">
            🎯 {tier_info['tier_name']} Negotiation Playbook
        </div>
        <div>{tier_info['negotiation_playbook']}</div>
        <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.4rem;">
            Equity Norms: <strong>{tier_info['equity_structure']}</strong> · Bonus Norms: <strong>{tier_info['variable_norm']}</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 5: RED-FLAG RADAR FROM REDDIT LAYER (1 LINE MAX)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

if rd_match_key:
    rf_data = reddit_benchmarks[rd_match_key].get("red_flags", {})
    np_days = rf_data.get("notice_period_days", tier_info["typical_notice_days"])
    b_risk = rf_data.get("bench_risk_level", "Moderate")
    pip_flag = "🚨 Active PIP/quota alerts reported" if rf_data.get("pip_quota_alert") else "Standard appraisal cycles"
    appr_str = rf_data.get("reported_appraisals", "3–6% merit hikes")
    rf_line = f"⚠️ <strong>{rd_match_key} Red Flags:</strong> {np_days}-day notice period · Bench risk: {b_risk} · PIP: {pip_flag} · Real appraisals: {appr_str}"
else:
    rf_line = f"⚠️ <strong>{tier_info['tier_name']} Norms:</strong> Typical notice period is {tier_info['typical_notice_days']} days. Verify signing bonus clawback windows and billability criteria."

st.markdown(f'<div class="alert-notice">{rf_line}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT 6: COMMUNITY OFFER INTEL (LIGHTWEIGHT THREAD & SUBMISSION)
# ═══════════════════════════════════════════════════════════════════════════════
target_comp_name = comp_match_key if comp_match_key else input_company.strip()
recent_notes = cn.get_notes(target_comp_name, detected_family, limit=3)

st.markdown(f'<div class="card-label">6. Community Offer Intel & Terms ({target_comp_name})</div>', unsafe_allow_html=True)

if recent_notes:
    for nt in recent_notes:
        st.markdown(
            f"""
            <div class="intel-bubble">
                <div style="font-size: 0.88rem; color: #1e293b; line-height: 1.45;">"{nt['note_text']}"</div>
                <div style="font-size: 0.76rem; color: #64748b; margin-top: 0.4rem;">🏷️ <strong>{nt['author_tag']}</strong> · {nt['role_family']} · Added {nt['created_at']}</div>
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
# OUTPUT 7: NEGOTIATION SUITE (3 SPECIALIZED TEMPLATES & SHARE CARD)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

tool_tab1, tool_tab2 = st.tabs(["📝 1-Click Negotiation Emails", "📤 WhatsApp / Mentor Share Card"])

with tool_tab1:
    st.caption("Select your negotiation scenario to generate an instant, high-converting counter-offer email:")
    email_mode = st.radio(
        "Negotiation Angle",
        ["1. Market Alignment (Anchor P75)", "2. Restructure Variable to Fixed", "3. Competing Offer Leverage"],
        horizontal=True,
    )

    if "Market Alignment" in email_mode:
        email_body = f"""Subject: Regarding the offer for {input_role} - {input_company}

Dear Hiring Team,

Thank you very much for extending the offer for the {input_role} position at {target_comp_name}. I am enthusiastic about the team's roadmap and the opportunity to contribute my {input_exp} years of experience in {detected_family}.

I reviewed the proposed package of ₹ {float(input_ctc):.1f} LPA CTC. Based on my research and current domain benchmarks for {detected_family} ({detected_seniority}), I would like to explore if we can align the total compensation closer to ₹ {c_targ:.1f} LPA.

This figure reflects market alignment for lateral hiring in this tier, and reaching this level would make my acceptance an immediate decision. I look forward to your thoughts.

Best regards,
[Your Name]"""
    elif "Restructure" in email_mode:
        email_body = f"""Subject: Regarding the compensation structure for {input_role} - {input_company}

Dear Hiring Team,

Thank you for extending the offer for {input_role} at {target_comp_name}. I am excited about joining the organization.

I noticed the offer of ₹ {float(input_ctc):.1f} LPA includes a {input_var_pct}% variable component. To ensure guaranteed monthly cash flow alignment, I would like to explore if we can either:
1. Adjust the fixed-to-variable ratio by bringing fixed pay closer to ₹ {c_targ:.1f} LPA, or
2. Add a one-time joining bonus to bridge the gap while maintaining your internal base pay bands.

I am eager to finalize terms and begin onboarding with the team.

Best regards,
[Your Name]"""
    else:
        email_body = f"""Subject: Regarding offer terms for {input_role} - {input_company}

Dear Hiring Team,

Thank you for the offer for the {input_role} role. {target_comp_name} remains my top choice due to the technical challenges and team culture.

I am currently in final stages with another organization offering compensation in the range of ₹ {c_strt:.1f} LPA. Because {target_comp_name} is my preferred destination, I would be prepared to decline competing discussions and sign immediately if we can align total compensation closer to ₹ {c_targ:.1f} LPA.

I would appreciate a brief call today to conclude our discussions.

Best regards,
[Your Name]"""

    st.code(email_body, language="markdown")

with tool_tab2:
    st.caption("Formatted summary to send to a mentor, peer, or group chat for a second opinion:")
    whatsapp_card = f"""📋 *Offer Review Request — {target_comp_name}*
• *Role:* {input_role} ({input_exp} YoE · {tier_info['tier_badge']})
• *Offered CTC:* ₹{float(input_ctc):.1f} LPA (Variable: {input_var_pct}%)
• *Net Monthly In-Hand:* ₹{int(low_mo/1000)}k – ₹{int(high_mo/1000)}k / mo (Budget 2024 New Tax Regime)
• *True Guaranteed Cash:* ₹{contract_audit['guaranteed_year1_cash_lpa']} LPA ({contract_audit['paper_inflation_gap_pct']}% Paper Gap)
• *Tier Standing:* {percentile}th percentile for {detected_family} ({detected_seniority})
• *80% Conformal Range:* ₹{conf_low}L – ₹{conf_high}L
• *Market Target Counter:* ₹{c_targ:.1f} LPA (+18%)
• *Contract Terms:* {rf_line.replace('<strong>', '').replace('</strong>', '')}

What do you think of these numbers?"""
    st.code(whatsapp_card, language="markdown")


# ── FOOTER & INDUSTRY CONTEXT ─────────────────────────────────────────────────
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.caption(
    "💡 **Looking for aggregate company-wide medians across 1.5M records?** "
    "Consult [Weekday's Salary Directory](https://www.weekday.works/salaries). "
    "This tool focuses specifically on evaluating this single offer's take-home pay, contract trap risks, and calibrated uncertainty."
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
        quick_th = calculate_take_home(predicted_market_ctc if 'predicted_market_ctc' in locals() else float(input_ctc))
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
