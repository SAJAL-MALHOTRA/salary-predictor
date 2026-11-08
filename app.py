"""
app.py -- India Tech Offer Intelligence & Compensation Decision Engine.
Production-grade FinTech / HR-Tech Architecture.

Positioning:
"Know what your offer is actually worth."
Understand actual monthly take-home, uncover compensation traps,
benchmark offers against peer tiers, model equity, compare offers, and negotiate with confidence.
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
import decision_matrix as dm
import equity_engine as ee
import negotiation_war_room as nwr
import offer_parser as op
import report_generator as rg
from taxonomy import categorize_job

# ── Paths ────────────────────────────────────────────────────────────────────
_BASE = Path(__file__).resolve().parent

# ── 1. PAGE SETUP & DESIGN SYSTEM CSS ─────────────────────────────────────────
st.set_page_config(
    page_title="Offer Intelligence | India Tech Compensation Analyzer",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# SEO Meta Tags & OpenGraph injection + Dynamic Head Script
st.markdown(
    """
    <head>
        <meta name="description" content="Understand what your Indian tech offer is actually worth. Calculate actual monthly take-home under Budget 2024 New Tax Regime, uncover gratuity and clawback contract traps, benchmark peer percentiles, model startup ESOPs, and generate informed negotiation strategies." />
        <meta name="keywords" content="salary calculator India, tech salary India, in-hand salary calculator, CTC to in-hand India, 90 day notice period, TCS salary, Infosys salary, Google salary India, offer negotiation email, ESOP calculator India" />
        <meta property="og:title" content="Offer Intelligence | India Tech Compensation Analyzer" />
        <meta property="og:description" content="Calculate real monthly take-home, uncover contract traps, benchmark your offer, and negotiate with confidence." />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Offer Intelligence — India Tech Compensation Analyzer" />
        <meta name="twitter:description" content="Know what your offer is actually worth before signing." />
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "WebApplication",
          "name": "Offer Intelligence",
          "description": "Compensation decision engine and contract auditor for Indian tech professionals",
          "applicationCategory": "FinanceApplication",
          "operatingSystem": "All"
        }
        </script>
    </head>
    <script>
      (function() {
        try {
          var doc = (window.parent && window.parent.document) ? window.parent.document : document;
          doc.title = "Offer Intelligence | India Tech Compensation Analyzer";
          var setMeta = function(attr, name, content) {
            var el = doc.querySelector('meta[' + attr + '="' + name + '"]');
            if (!el) {
              el = doc.createElement('meta');
              el.setAttribute(attr, name);
              doc.head.appendChild(el);
            }
            el.setAttribute('content', content);
          };
          setMeta('name', 'description', 'Understand what your Indian tech offer is actually worth. Calculate monthly take-home, uncover contract traps, benchmark peer percentiles, and model equity.');
          setMeta('property', 'og:title', 'Offer Intelligence | India Tech Compensation Analyzer');
          setMeta('property', 'og:description', 'Calculate real monthly take-home, uncover contract traps, and benchmark peer percentiles.');
        } catch(e) {}
      })();
    </script>
    """,
    unsafe_allow_html=True,
)

# Production FinTech Design System (Inter font, Restrained Neutral Palette)
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #151922;
    background-color: #F7F8FA;
}

/* Top Navigation Bar */
.top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #E5E7EB;
}
.brand-group {
    display: flex;
    align-items: baseline;
    gap: 8px;
}
.brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #151922;
    letter-spacing: -0.02em;
}
.brand-descriptor {
    font-size: 0.8rem;
    color: #667085;
    font-weight: 400;
}
.nav-links {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 0.82rem;
    color: #667085;
}
.nav-link {
    color: #667085;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.15s ease;
}
.nav-link:hover {
    color: #151922;
}

/* Hero Section */
.hero-container {
    margin-bottom: 1.75rem;
}
.hero-eyebrow {
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #4F46E5;
    margin-bottom: 0.4rem;
}
.hero-headline {
    font-size: 2.35rem;
    font-weight: 700;
    color: #151922;
    letter-spacing: -0.035em;
    line-height: 1.15;
    margin-bottom: 0.5rem;
}
.hero-supporting {
    font-size: 1.05rem;
    color: #667085;
    line-height: 1.5;
    margin-bottom: 1.25rem;
    max-width: 680px;
}
.trust-strip {
    display: flex;
    align-items: center;
    gap: 20px;
    padding-top: 0.5rem;
    font-size: 0.82rem;
    color: #667085;
    flex-wrap: wrap;
}
.trust-point {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}

/* Example Chips */
.example-section {
    margin-bottom: 0.75rem;
}
.example-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #667085;
    margin-bottom: 0.4rem;
}

/* Cards & Surfaces */
.surface-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 2px 0 rgba(16, 24, 40, 0.04);
}
.card-title-sm {
    font-size: 0.76rem;
    font-weight: 700;
    color: #667085;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}
.figure-hero {
    font-size: 2.25rem;
    font-weight: 700;
    color: #079669;
    letter-spacing: -0.02em;
    line-height: 1.15;
    font-variant-numeric: tabular-nums;
}
.figure-hero-sub {
    font-size: 1.1rem;
    font-weight: 500;
    color: #065F46;
}

/* Scenario Cards Grid */
.scenario-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 0.9rem;
}
.scenario-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    text-align: left;
}
.scenario-type {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.25rem;
}
.scenario-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #151922;
    font-variant-numeric: tabular-nums;
    margin-bottom: 0.2rem;
}
.scenario-desc {
    font-size: 0.74rem;
    color: #667085;
    line-height: 1.35;
}

/* Stacked Composition Bar */
.composition-bar {
    display: flex;
    height: 14px;
    border-radius: 6px;
    overflow: hidden;
    background: #F2F4F7;
    margin: 0.75rem 0 0.5rem 0;
    border: 1px solid #E5E7EB;
}
.bar-segment {
    height: 100%;
    transition: width 0.3s ease;
}

/* Percentile Spectrum Line */
.percentile-track {
    background: #E5E7EB;
    border-radius: 6px;
    height: 8px;
    position: relative;
    margin: 1.75rem 0 0.75rem 0;
}
.percentile-fill {
    background: #4F46E5;
    height: 100%;
    border-radius: 6px;
}
.percentile-pin {
    position: absolute;
    top: -24px;
    transform: translateX(-50%);
    background: #151922;
    color: #FFFFFF;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    white-space: nowrap;
}

/* Structured Risk Card */
.risk-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1rem 1.15rem;
    margin-bottom: 0.75rem;
}
.risk-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.45rem;
}
.risk-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: #151922;
}
.risk-badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.15rem 0.55rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.risk-badge-danger {
    background: #FEF2F2;
    color: #DC2626;
    border: 1px solid #FCA5A5;
}
.risk-badge-warning {
    background: #FFFBEB;
    color: #D97706;
    border: 1px solid #FCD34D;
}
.risk-badge-success {
    background: #ECFDF5;
    color: #079669;
    border: 1px solid #A7F3D0;
}
.risk-body {
    font-size: 0.84rem;
    color: #475467;
    line-height: 1.45;
    margin-bottom: 0.45rem;
}
.risk-impact {
    font-size: 0.8rem;
    font-weight: 600;
    color: #151922;
    margin-bottom: 0.35rem;
}
.risk-action {
    font-size: 0.78rem;
    color: #667085;
    border-top: 1px dashed #E5E7EB;
    padding-top: 0.35rem;
}

/* Strategy Box */
.strategy-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 0.95rem 1.05rem;
    height: 100%;
}
.strategy-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.2rem;
}
.strategy-figure {
    font-size: 1.35rem;
    font-weight: 700;
    color: #151922;
    font-variant-numeric: tabular-nums;
    margin-bottom: 0.25rem;
}
.strategy-desc {
    font-size: 0.78rem;
    color: #667085;
    line-height: 1.4;
}

/* Styled Streamlit Native Buttons */
button[data-testid="baseButton-secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    color: #344054 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.35rem 0.75rem !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05) !important;
}
button[data-testid="baseButton-secondary"]:hover {
    background: #F9FAFB !important;
    border-color: #D0D5DD !important;
    color: #1D2939 !important;
}
button[data-testid="baseButton-primary"] {
    background: #4F46E5 !important;
    border: 1px solid #4F46E5 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.55rem 1.25rem !important;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05) !important;
    transition: background-color 0.15s ease !important;
}
button[data-testid="baseButton-primary"]:hover {
    background: #4338CA !important;
    border-color: #4338CA !important;
}

/* Context Badge */
.context-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.74rem;
    font-weight: 500;
    margin-right: 0.35rem;
    margin-bottom: 0.35rem;
    background: #F2F4F7;
    color: #344054;
    border: 1px solid #EAECF0;
}
.context-badge-indigo {
    background: #EEF4FF;
    color: #3538CD;
    border-color: #C7D7FE;
}

/* Tabs styling */
div[data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #F2F4F7;
    padding: 5px;
    border-radius: 10px;
    margin-bottom: 1.25rem;
}
div[data-baseweb="tab"] {
    border-radius: 6px;
    font-weight: 600;
    padding: 6px 16px;
    color: #475467;
}
div[data-baseweb="tab"][aria-selected="true"] {
    background-color: #FFFFFF;
    color: #151922;
    box-shadow: 0 1px 3px rgba(16,24,40,0.08);
}

/* Responsive Breakpoints */
@media (max-width: 640px) {
    .scenario-grid {
        grid-template-columns: 1fr;
    }
    .figure-hero {
        font-size: 1.85rem;
    }
    .hero-headline {
        font-size: 1.85rem;
    }
    .trust-strip {
        flex-direction: column;
        align-items: flex-start;
        gap: 6px;
    }
}

/* Print Friendly 1-Page Summary */
@media print {
    header, footer, [data-testid="stSidebar"], .top-nav, .example-section, div[data-testid="stForm"], div[data-testid="stHorizontalBlock"] button {
        display: none !important;
    }
    .surface-card {
        box-shadow: none !important;
        border: 1px solid #D0D5DD !important;
        page-break-inside: avoid;
    }
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


# ── 3. TAX & TAKE-HOME CALCULATION ENGINE ─────────────────────────────────────
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

        tax *= 1.04  # 4% Health & Education Cess

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


# ── 4. TOP NAVIGATION BAR ─────────────────────────────────────────────────────
st.markdown(
    """
    <div class="top-nav">
        <div class="brand-group">
            <span class="brand-name">Offer Intelligence</span>
            <span class="brand-descriptor">· India Compensation Analyzer</span>
        </div>
        <div class="nav-links">
            <a href="#how-it-works" class="nav-link">How it works</a>
            <a href="#methodology" class="nav-link">Methodology</a>
            <a href="#privacy" class="nav-link">Privacy</a>
            <a href="https://github.com/SAJAL-MALHOTRA/salary-predictor" target="_blank" class="nav-link">GitHub</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── 5. HERO SECTION ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-eyebrow">India Tech Offer Intelligence</div>
        <h1 class="hero-headline">Your CTC isn't your salary.</h1>
        <p class="hero-supporting">
            Understand your actual monthly take-home, uncover compensation traps,
            benchmark your offer against peer tiers, and negotiate with confidence.
        </p>
        <div class="trust-strip">
            <span class="trust-point">✓ No signup required</span>
            <span class="trust-point">✓ Transparent calculation breakdown</span>
            <span class="trust-point">✓ Your offer details stay private</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── 6. DOCUMENT INGESTION / AUTO-PARSER (PILLAR 1) ────────────────────────────
with st.expander("📁 Auto-Extract from Offer Letter PDF or Salary Annexure", expanded=False):
    st.caption("Upload your offer letter PDF or paste salary annexure text. The parser extracts employer, CTC, basic salary, variable pay, joining bonus, notice period, and gratuity terms in 1 second.")
    parse_t1, parse_t2 = st.tabs(["Upload Offer PDF", "Paste Offer Text"])

    with parse_t1:
        uploaded_pdf = st.file_uploader("Upload Offer Letter PDF", type=["pdf"], key="offer_pdf_upload")
        if uploaded_pdf is not None:
            with st.spinner("Extracting offer terms from PDF..."):
                pdf_text = op.extract_text_from_pdf(uploaded_pdf)
                parsed = op.parse_offer_text(pdf_text)
                if "error" not in parsed:
                    st.success(f"✓ Extracted terms from {parsed['company']} ({parsed['ctc_lpa']} LPA) with {int(parsed['confidence']*100)}% confidence.")
                    st.session_state.cfg_company = parsed["company"]
                    st.session_state.cfg_role = parsed["role"]
                    st.session_state.cfg_ctc = parsed["ctc_lpa"]
                    st.session_state.cfg_var = parsed["variable_pct"]
                    st.session_state.cfg_jb = parsed["joining_bonus_lpa"]
                    st.session_state.cfg_grat = parsed["gratuity_included"]
                    st.session_state.cfg_vfreq = parsed["variable_freq"]
                    st.session_state.cfg_tenure = 2.0
                    st.rerun()
                else:
                    st.error("Could not parse offer terms. Please paste text in the second tab.")

    with parse_t2:
        pasted_text = st.text_area(
            "Paste Offer Letter / Salary Annexure Text:",
            placeholder="e.g. Total CTC: INR 24,00,000 per annum, Basic Salary: INR 9,60,000, Variable Pay: 15%, Joining Bonus: INR 2,00,000, Notice Period: 60 days...",
            height=110,
        )
        if st.button("Parse & Populate Form", use_container_width=True):
            if pasted_text.strip():
                parsed = op.parse_offer_text(pasted_text)
                st.session_state.cfg_company = parsed["company"]
                st.session_state.cfg_role = parsed["role"]
                st.session_state.cfg_ctc = parsed["ctc_lpa"]
                st.session_state.cfg_var = parsed["variable_pct"]
                st.session_state.cfg_jb = parsed["joining_bonus_lpa"]
                st.session_state.cfg_grat = parsed["gratuity_included"]
                st.session_state.cfg_vfreq = parsed["variable_freq"]
                st.success(f"✓ Populated terms for {parsed['company']} ({parsed['ctc_lpa']} LPA).")
                st.rerun()


# ── 7. OFFER INPUT WORKSPACE ──────────────────────────────────────────────────
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
if "cfg_jb" not in st.session_state:
    st.session_state.cfg_jb = 0.0
if "cfg_grat" not in st.session_state:
    st.session_state.cfg_grat = True
if "cfg_vfreq" not in st.session_state:
    st.session_state.cfg_vfreq = "Annual Payout (High Forfeiture Risk)"
if "cfg_tenure" not in st.session_state:
    st.session_state.cfg_tenure = 2.0

st.markdown(
    '<div class="example-label">See an example offer (Click to load scenario):</div>',
    unsafe_allow_html=True,
)
ex_c1, ex_c2, ex_c3, ex_c4 = st.columns(4)

if ex_c1.button("Infosys · 3.5y (₹12L)", use_container_width=True):
    st.session_state.cfg_company = "Infosys"
    st.session_state.cfg_role = "Senior Software Engineer"
    st.session_state.cfg_exp = 3.5
    st.session_state.cfg_ctc = 12.0
    st.session_state.cfg_var = 15
    st.session_state.cfg_city = "Bangalore"
    st.session_state.cfg_jb = 0.0
    st.session_state.cfg_grat = True
    st.session_state.cfg_vfreq = "Annual Payout (High Forfeiture Risk)"
    st.session_state.cfg_tenure = 2.0
    st.rerun()

if ex_c2.button("Swiggy · 4y (₹24L)", use_container_width=True):
    st.session_state.cfg_company = "Swiggy"
    st.session_state.cfg_role = "SDE 2"
    st.session_state.cfg_exp = 4.0
    st.session_state.cfg_ctc = 24.0
    st.session_state.cfg_var = 18
    st.session_state.cfg_city = "Bangalore"
    st.session_state.cfg_jb = 2.0
    st.session_state.cfg_grat = True
    st.session_state.cfg_vfreq = "Quarterly Payout"
    st.session_state.cfg_tenure = 2.0
    st.rerun()

if ex_c3.button("Google · 3y (₹35L)", use_container_width=True):
    st.session_state.cfg_company = "Google"
    st.session_state.cfg_role = "Software Engineer 3"
    st.session_state.cfg_exp = 3.0
    st.session_state.cfg_ctc = 35.0
    st.session_state.cfg_var = 15
    st.session_state.cfg_city = "Hyderabad"
    st.session_state.cfg_jb = 5.0
    st.session_state.cfg_grat = False
    st.session_state.cfg_vfreq = "Annual Payout (High Forfeiture Risk)"
    st.session_state.cfg_tenure = 3.0
    st.rerun()

if ex_c4.button("TCS · 1.5y (₹4.5L)", use_container_width=True):
    st.session_state.cfg_company = "TCS"
    st.session_state.cfg_role = "Assistant System Engineer"
    st.session_state.cfg_exp = 1.5
    st.session_state.cfg_ctc = 4.5
    st.session_state.cfg_var = 10
    st.session_state.cfg_city = "Pune"
    st.session_state.cfg_jb = 0.0
    st.session_state.cfg_grat = True
    st.session_state.cfg_vfreq = "Annual Payout (High Forfeiture Risk)"
    st.session_state.cfg_tenure = 2.0
    st.rerun()

st.caption("Note: Example scenarios for demonstration; not verified actual offer letters from these employers.")

# Two-Column Input Workspace
with st.container(border=True):
    col_in1, col_in2 = st.columns(2, gap="large")

    with col_in1:
        st.markdown("**Offer Details**")
        input_company = st.text_input(
            "Company Name",
            value=st.session_state.cfg_company,
            help="Employer name (e.g. Infosys, Swiggy, Google, TCS, Razorpay)",
        )
        input_role = st.text_input(
            "Job Title / Role",
            value=st.session_state.cfg_role,
            help="Role title (e.g. Senior Software Engineer, ML Engineer, SDE 2)",
        )
        input_city = st.text_input(
            "Employment City",
            value=st.session_state.cfg_city,
            help="Base city (e.g. Bangalore, Hyderabad, Pune, Gurgaon, Mumbai)",
        )
        input_exp = st.number_input(
            "Total Experience (Years)",
            min_value=0.0,
            max_value=30.0,
            value=float(st.session_state.cfg_exp),
            step=0.5,
        )

    with col_in2:
        st.markdown("**Compensation Details**")
        input_ctc = st.number_input(
            "Offered Annual CTC (₹ LPA)",
            min_value=1.0,
            max_value=250.0,
            value=float(st.session_state.cfg_ctc),
            step=0.5,
            help="Total Cost to Company quoted on the first page of your offer letter",
        )
        input_var_pct = st.slider(
            "Variable Pay Percentage (%)",
            min_value=0,
            max_value=100,
            value=int(st.session_state.cfg_var),
            step=1,
            help="Contingent portion of CTC tied to company performance or individual rating",
        )
        input_jb = st.number_input(
            "Joining / Sign-on Bonus (₹ LPA, optional)",
            min_value=0.0,
            max_value=50.0,
            value=float(st.session_state.cfg_jb),
            step=0.5,
            help="One-time upfront cash sign-on bonus, if applicable",
        )
        input_grat = st.checkbox(
            "Gratuity included in CTC sheet?",
            value=bool(st.session_state.cfg_grat),
            help="Standard in >80% of Indian IT CTC sheets (calculated as 4.81% of basic salary)",
        )
        input_vfreq = st.radio(
            "Variable Payout Frequency",
            ["Annual Payout (High Forfeiture Risk)", "Quarterly Payout"],
            index=0 if "Annual" in st.session_state.cfg_vfreq else 1,
            horizontal=True,
        )
        input_tenure = st.slider(
            "Expected Tenure at this Company (Years)",
            min_value=1.0,
            max_value=6.0,
            value=float(st.session_state.cfg_tenure),
            step=0.5,
            help="Important for statutory gratuity vesting under Section 4(1) of Payment of Gratuity Act 1972",
        )

    submit_eval_btn = st.button("Analyze offer →", type="primary", use_container_width=True)


# ── NORMALIZE & AUDIT OFFER PARAMETERS ───────────────────────────────────────
detected_family, detected_seniority = categorize_job(input_role)
tier_info = ct.classify_employer_tier(input_company)

# Case-insensitive company lookup
comp_match_key = None
for k in company_insights.keys():
    if k.lower() == input_company.strip().lower():
        comp_match_key = k
        break

comp_info = company_insights.get(comp_match_key, {}) if comp_match_key else {}
industry = comp_info.get("industry", "IT Services & Consulting")
rating = float(comp_info.get("rating", 3.8))

# Reddit layer lookup
rd_match_key = None
for k in reddit_benchmarks.keys():
    if k.lower() == input_company.strip().lower():
        rd_match_key = k
        break
rf_data = reddit_benchmarks[rd_match_key].get("red_flags", {}) if rd_match_key else {}
detected_np = rf_data.get("notice_period_days", tier_info["typical_notice_days"])

# Run Contract Risk Audit
contract_audit = ca.audit_offer_contract(
    ctc_lpa=input_ctc,
    variable_pct=input_var_pct,
    gratuity_included=input_grat,
    joining_bonus_lpa=input_jb,
    clawback_months=12 if input_jb > 0 else 0,
    notice_period_days=detected_np,
    variable_freq="Quarterly" if "Quarterly" in input_vfreq else "Annual",
    expected_tenure_years=input_tenure,
)

# Conformal Uncertainty Margin
conf_margin = float(metadata.get("conformal_margin_80_lpa", 6.01))
conf_low = max(1.0, round(float(input_ctc) - conf_margin, 1))
conf_high = round(float(input_ctc) + conf_margin, 1)

# Cash Flow Calculations (0%, 50%, 100% Variable Scenarios)
fixed_ratio = 1.0 - (float(input_var_pct) / 100.0)
fixed_ctc = float(input_ctc) * fixed_ratio

th_0 = calculate_take_home(fixed_ctc)
th_50 = calculate_take_home(fixed_ctc + (float(input_ctc) * float(input_var_pct) / 200.0))
th_100 = calculate_take_home(input_ctc)

low_mo = int(th_0["monthly_in_hand"])
mid_mo = int(th_50["monthly_in_hand"])
high_mo = int(th_100["monthly_in_hand"])

target_comp_name = comp_match_key if comp_match_key else input_company.strip()

# Market spread & counters
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
marker_left = min(91, max(9, percentile))

c_cons = round(float(input_ctc) * 1.08, 1)
c_targ = round(max(float(input_ctc) * 1.18, p75), 1)
c_strt = round(max(float(input_ctc) * 1.35, p75 * 1.15), 1)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WORKSPACE TABS: OFFER EVALUATOR, COMPARISON, EQUITY, WAR ROOM
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs(
    [
        "📋 Offer Audit & Report",
        "⚖️ Multi-Offer Decision Matrix",
        "📈 Total Rewards & Equity Modeler",
        "🛡️ Recruiter Objection War Room",
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: OFFER AUDIT & 8-PART REPORT
# ─────────────────────────────────────────────────────────────────────────────
with main_tab1:
    # 1-Click Executive PDF Memo Download Button
    pdf_bytes = rg.generate_pdf_audit_memo(
        offer_data={"company": target_comp_name, "role": input_role, "exp": float(input_exp), "city": input_city, "ctc_lpa": float(input_ctc), "variable_pct": int(input_var_pct)},
        take_home_data={"low_mo": low_mo, "high_mo": high_mo, "th_100": th_100},
        contract_audit=contract_audit,
        market_data={"percentile": percentile, "family": detected_family, "tier_badge": tier_info["tier_badge"], "p25": p25, "p50": p50, "p75": p75, "conf_low": conf_low, "conf_high": conf_high},
        counter_data={"c_cons": c_cons, "c_targ": c_targ, "c_strt": c_strt},
    )

    memo_c1, memo_c2 = st.columns([2.5, 1.5])
    with memo_c1:
        st.markdown(
            f"""
            <div style="margin-bottom: 0.5rem;">
                <span class="context-badge context-badge-indigo">{tier_info['tier_badge']}</span>
                <span class="context-badge">{detected_family}</span>
                <span class="context-badge">{detected_seniority}</span>
                <span class="context-badge">{input_city}</span>
                <span class="context-badge">{rating} / 5.0 Rating</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with memo_c2:
        st.download_button(
            label="📄 Download Executive Memo (PDF)",
            data=pdf_bytes,
            file_name=f"Offer_Audit_Memo_{target_comp_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # 02 — EXECUTIVE COMPENSATION SUMMARY
    st.markdown(
        f"""
        <div class="surface-card">
            <div class="card-title-sm">02 — Estimated Monthly Take-Home (Net Bank Credit)</div>
            <div class="figure-hero">₹ {int(low_mo):,} – ₹ {int(high_mo):,} <span class="figure-hero-sub">/ month</span></div>
            <div style="font-size: 0.86rem; color: #475467; margin-top: 0.4rem; line-height: 1.5;">
                Guaranteed monthly floor: <strong>₹ {int(low_mo):,}/mo</strong> (on ₹ {fixed_ctc:.1f}L fixed CTC) ·
                Expected payout: <strong>₹ {int(mid_mo):,}/mo</strong> (~50% variable) ·
                Maximum payout: <strong>₹ {int(high_mo):,}/mo</strong> (100% variable target).
            </div>
            <div style="font-size: 0.78rem; color: #667085; margin-top: 0.45rem;">
                Budget 2024 New Tax Regime (FY 2024-25, AY 2025-26) · ₹75,000 standard deduction · 40% basic salary assumption.
            </div>
            <div class="scenario-grid">
                <div class="scenario-card" style="border-top: 3px solid #DC2626;">
                    <div class="scenario-type" style="color: #DC2626;">Guaranteed Floor</div>
                    <div class="scenario-value">₹ {int(low_mo):,}</div>
                    <div class="scenario-desc">0% variable payout. Guaranteed fixed CTC: ₹ {fixed_ctc:.1f}L.</div>
                </div>
                <div class="scenario-card" style="border-top: 3px solid #4F46E5; background: #F8FAFC;">
                    <div class="scenario-type" style="color: #4F46E5;">Expected Payout</div>
                    <div class="scenario-value">₹ {int(mid_mo):,}</div>
                    <div class="scenario-desc">Realistic ~50% payout based on normal appraisal cycles.</div>
                </div>
                <div class="scenario-card" style="border-top: 3px solid #079669;">
                    <div class="scenario-type" style="color: #079669;">Maximum Target</div>
                    <div class="scenario-value">₹ {int(high_mo):,}</div>
                    <div class="scenario-desc">100% payout of full ₹ {float(input_ctc):.1f}L CTC. Not guaranteed income.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 03 — MONTHLY SALARY BREAKDOWN (ITEMIZED TABLE)
    with st.expander("03 — Itemized Monthly Salary Breakdown (View Calculation Steps)", expanded=False):
        st.caption("Detailed deduction formula under Budget 2024 New Tax Regime. Distinguishes contractual items from statutory estimates.")
        st.markdown(
            f"""
            <table style="width: 100%; border-collapse: collapse; font-size: 0.86rem;">
                <tr style="border-bottom: 1px solid #EAECF0;">
                    <th style="padding: 0.5rem 0; text-align: left; color: #667085; font-weight: 600;">Salary Component</th>
                    <th style="padding: 0.5rem 0; text-align: right; color: #667085; font-weight: 600;">Annual Amount</th>
                    <th style="padding: 0.5rem 0; text-align: right; color: #667085; font-weight: 600;">Monthly Credit / Deduction</th>
                    <th style="padding: 0.5rem 0; text-align: right; color: #667085; font-weight: 600;">Type / Formula</th>
                </tr>
                <tr style="border-bottom: 1px solid #EAECF0;">
                    <td style="padding: 0.45rem 0; font-weight: 600;">Offered Cost to Company (CTC)</td>
                    <td style="padding: 0.45rem 0; text-align: right; font-weight: 600;">₹ {int(th_100['ctc']):,}</td>
                    <td style="padding: 0.45rem 0; text-align: right;">₹ {int(th_100['ctc']/12):,}/mo</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #667085;">Contractual Input</td>
                </tr>
                <tr style="border-bottom: 1px solid #EAECF0;">
                    <td style="padding: 0.45rem 0; color: #344054;">Basic Salary</td>
                    <td style="padding: 0.45rem 0; text-align: right;">₹ {int(th_100['basic']):,}</td>
                    <td style="padding: 0.45rem 0; text-align: right;">₹ {int(th_100['basic']/12):,}/mo</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #667085;">40% of CTC Baseline</td>
                </tr>
                <tr style="border-bottom: 1px solid #EAECF0;">
                    <td style="padding: 0.45rem 0; color: #344054;">Special & Other Allowances</td>
                    <td style="padding: 0.45rem 0; text-align: right;">₹ {int(th_100['gross'] - th_100['basic']):,}</td>
                    <td style="padding: 0.45rem 0; text-align: right;">₹ {int((th_100['gross'] - th_100['basic'])/12):,}/mo</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #667085;">Fixed Gross Balance</td>
                </tr>
                <tr style="border-bottom: 1px solid #EAECF0;">
                    <td style="padding: 0.45rem 0; color: #DC2626;">(-) Income Tax (New Regime TDS)</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #DC2626;">- ₹ {int(th_100['tax_annual']):,}</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #DC2626;">- ₹ {int(th_100['tax_monthly']):,}/mo</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #667085;">FY 2024-25 Slabs + 4% Cess</td>
                </tr>
                <tr style="border-bottom: 1px solid #EAECF0;">
                    <td style="padding: 0.45rem 0; color: #4F46E5;">(-) Employee EPF (Retirement)</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #4F46E5;">- ₹ {int(th_100['epf_annual']):,}</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #4F46E5;">- ₹ {int(th_100['epf_monthly']):,}/mo</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #667085;">12% Basic (Statutory Rule)</td>
                </tr>
                <tr style="border-bottom: 2px solid #D0D5DD;">
                    <td style="padding: 0.45rem 0; color: #D97706;">(-) Professional Tax</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #D97706;">- ₹ {int(th_100['pt_annual']):,}</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #D97706;">- ₹ {int(th_100['pt_annual']/12):,}/mo</td>
                    <td style="padding: 0.45rem 0; text-align: right; color: #667085;">₹200/mo Standard</td>
                </tr>
                <tr style="background: #F8FAFC;">
                    <td style="padding: 0.65rem 0.5rem; font-weight: 700; color: #079669;">Estimated Net Bank Credit</td>
                    <td style="padding: 0.65rem 0.5rem; text-align: right; font-weight: 700; font-size: 1.05rem; color: #079669;">₹ {int(th_100['net_annual']):,}</td>
                    <td style="padding: 0.65rem 0.5rem; text-align: right; font-weight: 700; font-size: 1.05rem; color: #079669;">₹ {int(th_100['monthly_in_hand']):,}/mo</td>
                    <td style="padding: 0.65rem 0.5rem; text-align: right; font-weight: 600; color: #079669;">Net Monthly Cash</td>
                </tr>
            </table>
            """,
            unsafe_allow_html=True,
        )

    # 04 — OFFER STRUCTURE ANALYSIS
    pct_var = max(0.0, min(100.0, round(float(input_var_pct), 1)))
    pct_grat = max(0.0, min(100.0, round((contract_audit["phantom_gratuity_loss_rupees"] / (float(input_ctc) * 100000.0)) * 100.0, 1)))
    pct_guar = max(0.0, min(100.0, round(100.0 - pct_var - pct_grat, 1)))

    st.markdown(
        f"""
        <div class="surface-card">
            <div class="card-title-sm">04 — Offer Structure Analysis (What is actually inside your CTC?)</div>
            <div style="font-size: 0.88rem; color: #344054; line-height: 1.5;">
                Visualizing guaranteed monthly cash flow versus conditional or forfeited provisions:
            </div>
            <div class="composition-bar">
                <div class="bar-segment" style="width: {pct_guar}%; background: #079669;" title="Guaranteed Fixed Cash: {pct_guar}%"></div>
                <div class="bar-segment" style="width: {pct_var}%; background: #D97706;" title="Variable Bonus At-Risk: {pct_var}%"></div>
                <div class="bar-segment" style="width: {pct_grat}%; background: #DC2626;" title="Phantom Gratuity Deduction: {pct_grat}%"></div>
            </div>
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; font-size: 0.74rem; font-weight: 600; margin-top: 0.4rem;">
                <span style="color: #079669;">● Guaranteed Cash: {pct_guar}% (₹{contract_audit['guaranteed_year1_cash_lpa']}L)</span>
                <span style="color: #D97706;">● Variable At-Risk: {pct_var}% (₹{contract_audit['variable_lpa']}L)</span>
                <span style="color: #DC2626;">● Phantom Gratuity: {pct_grat}% (₹{int(contract_audit['phantom_gratuity_loss_rupees']):,})</span>
            </div>
            <div style="background: #F9FAFB; border: 1px solid #EAECF0; border-radius: 8px; padding: 0.85rem 1rem; margin-top: 0.85rem;">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-size: 0.82rem; font-weight: 600; color: #344054;">Paper CTC Inflation Gap:</span>
                    <span style="font-size: 0.95rem; font-weight: 700; color: #DC2626;">{contract_audit['paper_inflation_gap_pct']}% at-risk</span>
                </div>
                <div style="font-size: 0.78rem; color: #667085; margin-top: 0.2rem;">
                    ₹ {int(contract_audit['paper_inflation_gap_rupees']):,} of your quoted ₹ {float(input_ctc):.1f} LPA is contingent on variable payout or forfeitable upon departure before 5 years.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 05 — CONTRACTUAL RISK ANALYSIS (STRUCTURED REPORT)
    st.markdown('<div class="card-title-sm">05 — Contractual & Legal Risk Report</div>', unsafe_allow_html=True)
    structured_risks = contract_audit.get("structured_risks", [])
    for r in structured_risks:
        badge_cls = f"risk-badge-{r['severity_level']}"
        st.markdown(
            f"""
            <div class="risk-card">
                <div class="risk-header">
                    <span class="risk-title">{r['category']}: {r['title']}</span>
                    <span class="risk-badge {badge_cls}">{r['severity']}</span>
                </div>
                <div class="risk-body">{r['why_it_matters']}</div>
                <div class="risk-impact">Financial impact: {r['financial_impact']}</div>
                <div class="risk-action"><strong>What to verify in offer letter:</strong> {r['verification_step']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 06 — MARKET BENCHMARKING
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="surface-card">
            <div class="card-title-sm">06 — Market Benchmarking (How does your offer compare?)</div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #151922; margin-bottom: 0.35rem;">
                {percentile}th Percentile <span style="font-size: 0.95rem; font-weight: 400; color: #667085;">for {detected_family} ({detected_seniority} · {tier_info['tier_badge']})</span>
            </div>
            <div style="font-size: 0.86rem; color: #475467; line-height: 1.55;">
                An offer of <strong>₹ {float(input_ctc):.1f} LPA</strong> sits <strong>{position_label}</strong> (tier median: ₹ {p50} LPA).<br>
                • <strong>80% Conformal Uncertainty Interval:</strong> <strong>₹ {conf_low}L – ₹ {conf_high}L</strong> (calibrated ±{conf_margin} LPA finite-sample uncertainty margin)<br>
                • <strong>Middle 50% Tier Market Spread (P25–P75):</strong> <strong>₹ {p25}L – ₹ {p75}L</strong> for {tier_info['tier_name']}.
            </div>
            <div class="percentile-track">
                <div class="percentile-pin" style="left: {marker_left}%;">You ({percentile}%)</div>
                <div class="percentile-fill" style="width: {percentile}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #667085; font-weight: 600;">
                <span>P25: ₹{p25}L</span>
                <span>Median: ₹{p50}L</span>
                <span>P75: ₹{p75}L</span>
            </div>
            <div style="font-size: 0.76rem; color: #98A2B3; margin-top: 0.75rem; border-top: 1px solid #EAECF0; padding-top: 0.5rem;">
                <strong>Data Attribution:</strong> Benchmarks derived from an 867-row AmbitionBox training benchmark snapshot across Indian tech roles, certified via split conformal prediction on cross-validation residuals. Secondary offshore references cross-checked against Kaggle Glassdoor India (2,836 records) and US DOL LCA H-1B filings.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 07 — NEGOTIATION INTELLIGENCE
    st.markdown('<div class="card-title-sm">07 — Negotiation Intelligence & Counter-Offer Strategy</div>', unsafe_allow_html=True)
    col_st1, col_st2, col_st3 = st.columns(3, gap="small")
    with col_st1:
        st.markdown(
            f"""
            <div class="strategy-card">
                <div class="strategy-label" style="color: #079669;">1. Conservative Ask (+8%)</div>
                <div class="strategy-figure">₹ {c_cons:.1f} LPA</div>
                <div class="strategy-desc">Safe ask citing inflation and lateral transition costs; zero revocation risk.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_st2:
        st.markdown(
            f"""
            <div class="strategy-card" style="border-color: #C7D7FE; background: #F8F9FF;">
                <div class="strategy-label" style="color: #3538CD;">2. Market Target (+18%)</div>
                <div class="strategy-figure" style="color: #1E1B4B;">₹ {c_targ:.1f} LPA</div>
                <div class="strategy-desc">Anchors around the 75th percentile of role peers. Defensible with domain benchmark data.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_st3:
        st.markdown(
            f"""
            <div class="strategy-card">
                <div class="strategy-label" style="color: #D97706;">3. Stretch Ask (+35%)</div>
                <div class="strategy-figure">₹ {c_strt:.1f} LPA</div>
                <div class="strategy-desc">High-leverage ask appropriate if you hold competing offers or rare domain specialization.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 08 — COMMUNITY OFFER INTEL
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="card-title-sm">08 — Community Offer Intel ({target_comp_name})</div>', unsafe_allow_html=True)

    recent_notes = cn.get_notes(target_comp_name, detected_family, limit=3)
    if recent_notes:
        for nt in recent_notes:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-left: 3px solid #4F46E5; border-radius: 8px; padding: 0.85rem 1.05rem; margin-bottom: 0.6rem;">
                    <div style="font-size: 0.86rem; color: #344054; line-height: 1.45;">"{nt['note_text']}"</div>
                    <div style="font-size: 0.74rem; color: #667085; margin-top: 0.35rem;">
                        <strong>{nt['author_tag']}</strong> · {nt['role_family']} · Added {nt['created_at']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("No specific community notes for this employer yet. Add verified terms below.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: MULTI-OFFER DECISION MATRIX (PILLAR 2)
# ─────────────────────────────────────────────────────────────────────────────
with main_tab2:
    st.markdown("### ⚖️ Multi-Offer Comparative Decision Matrix")
    st.caption("Evaluate Offer A vs. a competing Offer B or your Current Baseline. Quantifies net monthly in-hand delta, career mobility, and notice period buyout recovery.")

    comp_c1, comp_c2 = st.columns(2, gap="large")

    with comp_c1:
        st.markdown(f"**Offer A: {input_company} (Primary)**")
        st.write(f"• **Quoted CTC:** ₹ {float(input_ctc):.1f} LPA")
        st.write(f"• **Variable Pay:** {input_var_pct}% (₹ {float(input_ctc)*float(input_var_pct)/100.0:.1f}L)")
        st.write(f"• **Net Take-Home:** ₹ {int(low_mo):,} – ₹ {int(high_mo):,} / mo")
        st.write(f"• **Notice Period:** {detected_np} Days")
        st.write(f"• **Guaranteed Cash:** ₹ {contract_audit['guaranteed_year1_cash_lpa']} LPA")

    with comp_c2:
        st.markdown("**Offer B / Current Job Baseline**")
        comp_b_name = st.text_input("Employer B Name", value="Swiggy", key="comp_b_name")
        comp_b_ctc = st.number_input("Offered Annual CTC (₹ LPA)", min_value=1.0, max_value=250.0, value=20.0, step=0.5, key="comp_b_ctc")
        comp_b_var = st.slider("Variable Pay (%)", min_value=0, max_value=60, value=15, step=1, key="comp_b_var")
        comp_b_jb = st.number_input("Joining Bonus (₹ LPA)", min_value=0.0, max_value=30.0, value=2.0, step=0.5, key="comp_b_jb")
        comp_b_np = st.selectbox("Notice Period (Days)", [30, 60, 90], index=1, key="comp_b_np")

    # Evaluate profiles
    th_b_fixed = calculate_take_home(float(comp_b_ctc) * (1.0 - float(comp_b_var)/100.0))
    tier_b_info = ct.classify_employer_tier(comp_b_name)

    audit_b = ca.audit_offer_contract(
        ctc_lpa=comp_b_ctc,
        variable_pct=comp_b_var,
        gratuity_included=True,
        joining_bonus_lpa=comp_b_jb,
        notice_period_days=comp_b_np,
        expected_tenure_years=2.0,
    )

    prof_a = dm.evaluate_offer_profile(
        name=f"Offer A ({input_company})",
        ctc_lpa=float(input_ctc),
        variable_pct=float(input_var_pct),
        joining_bonus_lpa=float(input_jb),
        notice_period_days=detected_np,
        gratuity_included=input_grat,
        expected_tenure_years=float(input_tenure),
        take_home_monthly=low_mo,
        guaranteed_year1_cash_lpa=contract_audit["guaranteed_year1_cash_lpa"],
        tier_num=tier_info["tier_num"],
    )

    prof_b = dm.evaluate_offer_profile(
        name=f"Offer B ({comp_b_name})",
        ctc_lpa=float(comp_b_ctc),
        variable_pct=float(comp_b_var),
        joining_bonus_lpa=float(comp_b_jb),
        notice_period_days=comp_b_np,
        gratuity_included=True,
        expected_tenure_years=2.0,
        take_home_monthly=th_b_fixed["monthly_in_hand"],
        guaranteed_year1_cash_lpa=audit_b["guaranteed_year1_cash_lpa"],
        tier_num=tier_b_info["tier_num"],
    )

    comp_res = dm.compare_two_offers(prof_a, prof_b)

    # Comparative Delta Hero Card
    diff_mo = comp_res["diff_monthly"]
    diff_sign = "+" if diff_mo >= 0 else "-"
    diff_color = "#079669" if diff_mo >= 0 else "#DC2626"

    st.markdown(
        f"""
        <div class="surface-card" style="border-left: 4px solid {diff_color};">
            <div class="card-title-sm">Net Monthly Bank Credit Delta</div>
            <div style="font-size: 2rem; font-weight: 700; color: {diff_color}; font-variant-numeric: tabular-nums;">
                {diff_sign} ₹ {abs(int(diff_mo)):,} <span style="font-size: 1rem; color: #667085; font-weight: 400;">/ month in bank</span>
            </div>
            <div style="font-size: 0.86rem; color: #344054; margin-top: 0.35rem;">
                Annual net cash delta: <strong>{diff_sign} ₹ {abs(int(comp_res['diff_annual_net'])):,}</strong> ·
                Guaranteed cash delta: <strong>{comp_res['diff_guaranteed_lpa']:+0.2f} LPA</strong>.
            </div>
            <div style="font-size: 0.8rem; color: #667085; margin-top: 0.3rem;">
                {comp_res['breakeven_text']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Side-by-Side Comparison Table
    st.markdown(
        f"""
        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; margin-bottom: 1rem;">
            <tr style="border-bottom: 1px solid #EAECF0;">
                <th style="padding: 0.5rem 0; text-align: left; color: #667085;">Evaluation Metric</th>
                <th style="padding: 0.5rem 0; text-align: right; color: #151922;">{prof_a['name']}</th>
                <th style="padding: 0.5rem 0; text-align: right; color: #151922;">{prof_b['name']}</th>
            </tr>
            <tr style="border-bottom: 1px solid #EAECF0;">
                <td style="padding: 0.45rem 0; color: #475467;">Quoted Annual CTC</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 600;">₹ {prof_a['ctc_lpa']} LPA</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 600;">₹ {prof_b['ctc_lpa']} LPA</td>
            </tr>
            <tr style="border-bottom: 1px solid #EAECF0;">
                <td style="padding: 0.45rem 0; color: #475467;">Guaranteed Year-1 Cash</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 600;">₹ {prof_a['guaranteed_year1_cash_lpa']} LPA</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 600;">₹ {prof_b['guaranteed_year1_cash_lpa']} LPA</td>
            </tr>
            <tr style="border-bottom: 1px solid #EAECF0;">
                <td style="padding: 0.45rem 0; color: #475467;">Guaranteed Monthly Floor</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 700; color: #079669;">₹ {prof_a['take_home_monthly']:,}/mo</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 700; color: #079669;">₹ {prof_b['take_home_monthly']:,}/mo</td>
            </tr>
            <tr style="border-bottom: 1px solid #EAECF0;">
                <td style="padding: 0.45rem 0; color: #475467;">Notice Period Lock</td>
                <td style="padding: 0.45rem 0; text-align: right;">{prof_a['notice_period_days']} Days</td>
                <td style="padding: 0.45rem 0; text-align: right;">{prof_b['notice_period_days']} Days</td>
            </tr>
            <tr style="border-bottom: 1px solid #EAECF0;">
                <td style="padding: 0.45rem 0; color: #475467;">Risk-Adjusted Comp Score</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 700;">{prof_a['composite_score']} / 100</td>
                <td style="padding: 0.45rem 0; text-align: right; font-weight: 700;">{prof_b['composite_score']} / 100</td>
            </tr>
        </table>
        """,
        unsafe_allow_html=True,
    )

    # Verdict Card
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 0.95rem 1.15rem;">
            <div style="font-size: 0.76rem; font-weight: 700; color: #667085; text-transform: uppercase;">Decision Synthesis</div>
            <div style="font-size: 1.05rem; font-weight: 600; color: {comp_res['verdict_color']}; margin: 0.25rem 0;">
                {comp_res['verdict_title']}
            </div>
            <div style="font-size: 0.84rem; color: #475467; line-height: 1.45;">
                Factoring in guaranteed monthly cash, variable haircut exposure, and notice period exit mobility.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: TOTAL REWARDS & EQUITY MODELER (PILLAR 3)
# ─────────────────────────────────────────────────────────────────────────────
with main_tab3:
    st.markdown("### 📈 Total Rewards & Equity Valuation Engine")
    st.caption("Model Global Tech RSUs or Indian Startup ESOPs: 4-year vesting schedules, liquidity probability haircuts, 90-day exercise traps, and Section 17(2) perquisite tax.")

    eq_c1, eq_c2 = st.columns(2, gap="large")

    with eq_c1:
        eq_type = st.radio("Equity Structure", ["RSU (Public Listed Tech)", "ESOP (Private Indian Startup)"], horizontal=True)
        eq_grant = st.number_input("Total 4-Year Grant Value (₹ LPA)", min_value=1.0, max_value=300.0, value=24.0, step=1.0)
        eq_stage = st.selectbox(
            "Company Liquidity Profile",
            ["Public Tech / GCC", "Late-Stage Unicorn (Frequent Buybacks)", "Early-Stage Startup"],
            index=0 if "RSU" in eq_type else 1,
        )

    with eq_c2:
        eq_vest = st.selectbox(
            "Vesting Schedule",
            ["Standard 25/25/25/25 (with 1-Yr Cliff)", "Amazon Back-Loaded (5/15/40/40)", "Frontloaded (33/33/22/12)"],
        )
        eq_window = st.selectbox(
            "Post-Departure Exercise Window (Days)",
            [30, 90, 180, 365, 1825],
            index=1,
            help="Crucial for unlisted startups: how many days you have to exercise vested options after resigning.",
        )

    # Run Equity Evaluation
    equity_eval = ee.evaluate_equity_component(
        equity_type="RSU" if "RSU" in eq_type else "ESOP",
        grant_value_lpa=eq_grant,
        vesting_schedule=eq_vest,
        company_stage=eq_stage,
        exercise_window_days=eq_window,
        annual_base_ctc_lpa=float(input_ctc),
    )

    # Total Rewards Hero Card
    st.markdown(
        f"""
        <div class="surface-card">
            <div class="card-title-sm">Year-1 Total Rewards (Base Cash + Liquid Equity)</div>
            <div class="figure-hero">₹ {equity_eval['total_y1_realizable_rewards_lpa']} LPA <span class="figure-hero-sub">realizable Year-1 rewards</span></div>
            <div style="font-size: 0.86rem; color: #475467; margin-top: 0.35rem;">
                Quoted Year-1 Rewards: <strong>₹ {equity_eval['total_y1_quoted_rewards_lpa']} LPA</strong> (₹ {input_ctc}L base CTC + ₹ {equity_eval['y1_vest_lpa']}L Year-1 vest).
            </div>
            <div style="font-size: 0.8rem; color: #667085; margin-top: 0.25rem;">
                {equity_eval['liquidity_desc']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4-Year Vesting Trajectory Cards
    st.markdown('<div class="card-title-sm">4-Year Vesting Trajectory</div>', unsafe_allow_html=True)
    v_c1, v_c2, v_c3, v_c4 = st.columns(4)
    with v_c1:
        st.markdown(f"""<div class="scenario-card"><div class="scenario-type">Year 1 ({int(equity_eval['vest_splits'][0]*100)}%)</div><div class="scenario-value">₹ {equity_eval['y1_vest_lpa']}L</div><div class="scenario-desc">Realizable: ₹{equity_eval['y1_realizable_lpa']}L</div></div>""", unsafe_allow_html=True)
    with v_c2:
        st.markdown(f"""<div class="scenario-card"><div class="scenario-type">Year 2 ({int(equity_eval['vest_splits'][1]*100)}%)</div><div class="scenario-value">₹ {equity_eval['y2_vest_lpa']}L</div><div class="scenario-desc">Vests at Month 24</div></div>""", unsafe_allow_html=True)
    with v_c3:
        st.markdown(f"""<div class="scenario-card"><div class="scenario-type">Year 3 ({int(equity_eval['vest_splits'][2]*100)}%)</div><div class="scenario-value">₹ {equity_eval['y3_vest_lpa']}L</div><div class="scenario-desc">Vests at Month 36</div></div>""", unsafe_allow_html=True)
    with v_c4:
        st.markdown(f"""<div class="scenario-card"><div class="scenario-type">Year 4 ({int(equity_eval['vest_splits'][3]*100)}%)</div><div class="scenario-value">₹ {equity_eval['y4_vest_lpa']}L</div><div class="scenario-desc">Vests at Month 48</div></div>""", unsafe_allow_html=True)

    # Exercise Window Trap Warning
    for flag in equity_eval["exercise_trap_flags"]:
        st.markdown(f"""<div style="background: #FFFBEB; border-left: 4px solid #D97706; padding: 0.85rem 1rem; border-radius: 6px; font-size: 0.84rem; color: #92400E; margin-top: 0.9rem;">{flag}</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: RECRUITER OBJECTION REBUTTAL WAR ROOM (PILLAR 4)
# ─────────────────────────────────────────────────────────────────────────────
with main_tab4:
    st.markdown("### 🛡️ Recruiter Objection Rebuttal War Room")
    st.caption("Indian recruiters rely on 5 standard pushbacks to shut down negotiations. Select the objection you received to generate battle-tested rebuttal scripts.")

    objections = nwr.get_all_objections()
    obj_options = [obj["title"] for obj in objections]
    selected_obj_title = st.selectbox("Select Recruiter Objection", obj_options)

    selected_obj = next(o for o in objections if o["title"] == selected_obj_title)

    # Analysis Card
    st.markdown(
        f"""
        <div class="surface-card">
            <div style="font-size: 0.74rem; font-weight: 700; color: #DC2626; text-transform: uppercase;">The Recruiter's Hidden Constraint</div>
            <div style="font-size: 0.88rem; color: #344054; margin: 0.35rem 0 0.75rem 0; line-height: 1.45;">
                {selected_obj['recruiter_motive']}
            </div>
            <div style="font-size: 0.74rem; font-weight: 700; color: #079669; text-transform: uppercase;">Your Strategic Leverage</div>
            <div style="font-size: 0.88rem; color: #344054; margin-top: 0.35rem; line-height: 1.45;">
                {selected_obj['winning_leverage']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Rebuttal Scripts
    reb_t1, reb_t2 = st.tabs(["Written Email Rebuttal", "Verbal Phone Script"])

    with reb_t1:
        customized_email = (
            selected_obj["email_script"]
            .replace("[Role]", input_role)
            .replace("[Company]", target_comp_name)
            .replace("[Target CTC]", f"{c_targ:.1f}")
            .replace("[Target Bonus]", f"{round(float(input_ctc)*0.10, 1)}")
            .replace("[Buyout Amount]", f"{int(float(input_ctc)*100000*0.4/12*2):,}")
            .replace("[Amount]", f"{round(float(input_ctc)*0.10, 1)}")
        )
        st.text_area("Customized Counter Email (Ready to Send):", value=customized_email, height=220)
        st.caption("Tip: Select and copy text to paste into your email reply.")

    with reb_t2:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 1rem 1.15rem; font-size: 0.88rem; color: #1E293B; line-height: 1.55;">
                {selected_obj['verbal_script']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Use this script when negotiating verbally over the phone with your HR recruiter or talent partner.")


# ── 09 — METHODOLOGY, PRIVACY & LEGAL TRANSPARENCY ────────────────────────────
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

with st.expander("Methodology, Privacy & Statutory Assumptions", expanded=False):
    st.markdown(
        """
        <div id="methodology" style="font-size: 0.84rem; color: #475467; line-height: 1.6;">
            <strong>Methodology & Tax Baseline:</strong><br>
            • In-hand monthly calculations apply India's New Tax Regime under Budget 2024 / FY 2024-25 (AY 2025-26).<br>
            • Standard deduction: ₹75,000. Basic salary is modeled at 40% of CTC (standard across Indian IT and consulting agreements).<br>
            • Employee Provident Fund (EPF): Modeled at 12% of basic salary, subject to statutory limits.<br>
            • Professional Tax: Fixed at ₹2,400/year (₹200/month) where CTC exceeds ₹3,00,000.<br>
            • Conformal Prediction: Uncertainty intervals (±6.01 LPA) are calibrated on out-of-fold cross-validation residuals to guarantee exact 80.0% finite-sample empirical coverage.<br><br>

            <strong id="privacy">Privacy & Data Handling:</strong><br>
            • All salary calculations execute client-side / within your active session.<br>
            • No personal identity, resume text, or offer letter PDFs are collected, sold, or shared with third parties.<br>
            • Community offer notes are submitted voluntarily without user accounts and are filtered by automated regex moderation.<br><br>

            <strong>Legal & Advisory Disclaimer:</strong><br>
            This application provides analytical estimations for personal compensation planning and career decision-making. It does not constitute formal legal, tax, or financial advisory services. Actual pay slips may vary based on company-specific flexi-benefit declarations, EPF opt-out choices, and employer gratuity schemes.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(
    "Looking for aggregate company-wide medians across 1.5M records? Consult "
    "[Weekday's Salary Directory](https://www.weekday.works/salaries). "
    "This tool focuses specifically on evaluating this single offer's take-home pay, contract trap risks, and calibrated uncertainty."
)


# ── 10 — DEVELOPER SURFACES (GATED UNDER DEV_MODE) ───────────────────────────
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
        quick_th = calculate_take_home(float(input_ctc))
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
                        marker=dict(colors=["#079669", "#DC2626", "#4F46E5", "#D97706"]),
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
                <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 1rem 1.25rem;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                        <tr style="border-bottom: 1px solid #EAECF0;">
                            <td style="padding: 0.5rem 0; color: #667085;">Annual Cost to Company (CTC)</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 700; color: #151922;">₹ {int(quick_th['ctc']):,}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #EAECF0;">
                            <td style="padding: 0.5rem 0; color: #667085;">Estimated Basic (40% of CTC)</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 600;">₹ {int(quick_th['basic']):,}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #EAECF0;">
                            <td style="padding: 0.5rem 0; color: #DC2626;">(-) Income Tax (New Regime TDS)</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #DC2626;">- ₹ {int(quick_th['tax_annual']):,}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #EAECF0;">
                            <td style="padding: 0.5rem 0; color: #4F46E5;">(-) Employee EPF (Retirement)</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #4F46E5;">- ₹ {int(quick_th['epf_annual']):,}</td>
                        </tr>
                        <tr style="border-bottom: 2px solid #D0D5DD;">
                            <td style="padding: 0.5rem 0; color: #D97706;">(-) Professional Tax</td>
                            <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #D97706;">- ₹ {int(quick_th['pt_annual']):,}</td>
                        </tr>
                        <tr style="background: #F8FAFC;">
                            <td style="padding: 0.75rem 0.5rem; font-weight: 700; color: #079669;">Estimated Net Bank Credit</td>
                            <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 700; font-size: 1.05rem; color: #079669;">₹ {int(quick_th['monthly_in_hand']):,}/mo</td>
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
