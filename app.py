"""
app.py -- India Salary & Career Intelligence Platform.

Redesigned with modern, responsive UI/UX design system:
- High-impact on-page Estimator Hero Card (no hidden controls)
- Live Monthly Take-Home & New Tax Regime breakdown alongside CTC
- 3 focused navigation modules (Salary Hub, Offer Comparison, AI Review Copilot)
- Custom typography, pill badges, and clean Plotly charts
- Voting Ensemble ML (RandomForest + HistGradientBoosting) with NLP Role Normalization
"""

import json
import os
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Paths ────────────────────────────────────────────────────────────────────
_BASE = Path(__file__).resolve().parent

# ── 1. PAGE SETUP & DESIGN SYSTEM CSS ────────────────────────────────────────
st.set_page_config(
    page_title="India Salary & Career Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",  # Clean by default; essential controls are on-page!
)

# Custom Design System CSS
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
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.3rem 0.8rem;
    border-radius: 9999px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.app-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 0.25rem;
}
.app-subtitle {
    font-size: 1.05rem;
    color: #64748b;
    margin-bottom: 1.5rem;
}

/* Cards */
.metric-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    height: 100%;
}
.metric-box-highlight {
    background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
    border: 1px solid #bbf7d0;
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 2px 6px rgba(16, 185, 129, 0.06);
    height: 100%;
}
.metric-caption {
    font-size: 0.75rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
}
.metric-val-ctc {
    font-size: 2.3rem;
    font-weight: 800;
    color: #1e1b4b;
    line-height: 1.1;
}
.metric-val-inhand {
    font-size: 2.3rem;
    font-weight: 800;
    color: #047857;
    line-height: 1.1;
}
.metric-sub {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 0.35rem;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}
.badge-indigo { background: #e0e7ff; color: #4338ca; }
.badge-emerald { background: #d1fae5; color: #065f46; }
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-slate { background: #f1f5f9; color: #475569; }

/* Culture Quotes */
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

/* Tabs */
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
    if insights_file.exists():
        with open(insights_file, "r", encoding="utf-8") as f:
            company_insights = json.load(f)
    else:
        company_insights = {}

    return pipeline, metadata, df, company_insights


pipeline, metadata, df, company_insights = load_assets()

companies = metadata["companies"]
company_jobs = metadata["company_jobs"]
all_job_titles = metadata["all_job_titles"]
role_families = metadata.get("role_families", sorted(df["Role_Family"].unique().tolist()))
seniority_levels = metadata.get("seniority_levels", ["Entry / Junior", "Mid-Level", "Senior / Lead", "Manager / Lead", "Executive / Director"])
experience_cap = float(metadata["experience_cap"])


# ── 3. NLP & UTILITY FUNCTIONS ───────────────────────────────────────────────
def categorize_job(title: str):
    """Map noisy job titles into canonical Role Family & Seniority Level."""
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


def get_tree_predictions(pl, input_df):
    """Extract individual tree predictions from the Random Forest component in VotingRegressor."""
    preprocessed = pl.named_steps["preprocessor"].transform(input_df)
    voting = pl.named_steps["regressor"]
    rf = voting.named_estimators_["rf"]
    return np.array([tree.predict(preprocessed)[0] for tree in rf.estimators_])


def find_comparable_records(dataframe, company, job_title, role_family, experience, n=8):
    """Score and rank dataset rows by relevance to user query."""
    title_match = dataframe["Job_Title"] == job_title
    family_match = dataframe["Role_Family"] == role_family
    comp_match = dataframe["Company"] == company

    scores = title_match.astype(int) * 4.0 + family_match.astype(int) * 3.0 + comp_match.astype(int) * 2.5
    exp_diff = (dataframe["Avg_Exp"] - experience).abs()
    scores = scores - (exp_diff / 5.0)

    top_indices = scores.nlargest(n).index
    return dataframe.loc[top_indices].copy()


def calculate_take_home(ctc_lpa):
    """
    Compute estimated in-hand salary under India's New Tax Regime (Budget 2024 / FY 2024-25 & 2025-26).
    Standard deduction: ₹75,000.
    """
    ctc = float(ctc_lpa) * 100000.0
    basic = ctc * 0.40

    if basic * 0.12 > 1800 * 12 and ctc > 1500000:
        epf_annual = 1800 * 12
    else:
        epf_annual = basic * 0.12

    gross_salary = ctc - epf_annual
    pt_annual = 2400.0 if ctc >= 300000 else 0.0

    # New Tax Regime FY 2024-25 / FY 2025-26
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
st.markdown('<div class="header-badge">🇮🇳 Compensation & Career Intelligence</div>', unsafe_allow_html=True)
st.markdown('<h1 class="app-title">India Salary & Career Platform</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-subtitle">Real market benchmarks, monthly take-home tax breakdowns, and AI review synthesis powered by AmbitionBox data.</p>',
    unsafe_allow_html=True,
)


# ── 5. ON-PAGE HERO ESTIMATOR (Front and Center UX) ──────────────────────────
with st.container(border=True):
    col_in1, col_in2, col_in3 = st.columns([1.3, 1.8, 1.4], gap="medium")

    with col_in1:
        selected_company = st.selectbox(
            "🏢 Select Company",
            companies,
            index=companies.index("TCS") if "TCS" in companies else 0,
            help="Choose from 118 verified employers",
        )

    with col_in2:
        # Default to company's roles, but allow searching all
        company_specific = company_jobs.get(selected_company, all_job_titles)
        role_choices = company_specific if company_specific else all_job_titles
        default_role_idx = 0
        if "Software Developer" in role_choices:
            default_role_idx = role_choices.index("Software Developer")
        elif "Software Engineer" in role_choices:
            default_role_idx = role_choices.index("Software Engineer")

        selected_job = st.selectbox(
            "👤 Job Title",
            role_choices,
            index=default_role_idx,
            help="Choose from roles reported at this company",
        )

    with col_in3:
        selected_exp = st.slider(
            "📅 Total Experience",
            min_value=0.0,
            max_value=experience_cap,
            value=min(4.0, experience_cap),
            step=0.5,
            format="%.1f yrs",
        )

    # Contextual tags right under the inputs
    detected_family, detected_seniority = categorize_job(selected_job)
    comp_info = company_insights.get(selected_company, {})
    industry = comp_info.get("industry", "Corporate")
    rating = float(comp_info.get("rating", 3.5))
    hq_city = comp_info.get("hq_city", "India")
    reviews_count = comp_info.get("reviews", "10k+")

    st.markdown(
        f"""
        <div style="margin-top: 0.3rem;">
            <span class="badge badge-indigo">Domain: {detected_family}</span>
            <span class="badge badge-slate">Level: {detected_seniority}</span>
            <span class="badge badge-amber">⭐ {rating} / 5.0 Rating</span>
            <span class="badge badge-slate">🏭 {industry}</span>
            <span class="badge badge-slate">📍 {hq_city}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── 6. MODEL INFERENCE & HERO METRICS ────────────────────────────────────────
user_input_df = pd.DataFrame(
    [
        {
            "Company": selected_company,
            "Job_Title": selected_job,
            "Industry": industry,
            "Role_Family": detected_family,
            "Seniority_Level": detected_seniority,
            "Rating": rating,
            "Avg_Exp": float(selected_exp),
        }
    ]
)

predicted_salary = round(float(pipeline.predict(user_input_df)[0]), 1)
tree_predictions = get_tree_predictions(pipeline, user_input_df)
p10 = round(float(np.percentile(tree_predictions, 10)), 1)
p90 = round(float(np.percentile(tree_predictions, 90)), 1)
std_dev = round(float(np.std(tree_predictions)), 1)
quick_th = calculate_take_home(predicted_salary)
exact_matches = df[(df["Company"] == selected_company) & (df["Job_Title"] == selected_job)]

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# 3-Column Executive Hero Cards
card_col1, card_col2, card_col3 = st.columns([1.3, 1.3, 1.4], gap="medium")

with card_col1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-caption">Predicted Annual CTC</div>
            <div class="metric-val-ctc">₹ {predicted_salary} <span style="font-size: 1.2rem; font-weight:600; color:#64748b;">LPA</span></div>
            <div class="metric-sub">Likely Range: <strong>₹ {p10} - {p90} LPA</strong> (±{std_dev}L)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_col2:
    st.markdown(
        f"""
        <div class="metric-box-highlight">
            <div class="metric-caption">Estimated In-Hand Pay</div>
            <div class="metric-val-inhand">₹ {int(quick_th['monthly_in_hand']):,} <span style="font-size: 1.1rem; font-weight:600; color:#065f46;">/ mo</span></div>
            <div class="metric-sub">Annual Net: <strong>₹ {int(quick_th['net_annual']/100000):.1f} Lakhs</strong> (New Tax Regime)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card_col3:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-caption">Employer Intelligence ({selected_company})</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #0f172a; margin-bottom: 0.3rem;">
                ⭐ {rating} / 5.0 <span style="font-size: 0.85rem; color:#64748b; font-weight: 500;">({reviews_count} reviews)</span>
            </div>
            <div class="metric-sub">HQ: <strong>{hq_city}</strong> · Sector: <strong>{industry}</strong> · Median: <strong>₹ {comp_info.get('median_salary', 'N/A')} LPA</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Ground Truth Verification Notice
if len(exact_matches) > 0:
    amb_min = exact_matches["Min_Salary_LPA"].min()
    amb_max = exact_matches["Max_Salary_LPA"].max()
    amb_avg = exact_matches["Avg_Salary_LPA"].mean()
    rep_exp = exact_matches["Experience"].iloc[0]
    st.markdown(
        f"""
        <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 10px; padding: 0.7rem 1rem; margin-top: 0.8rem; font-size: 0.88rem; color: #065f46;">
            ✅ <strong>Verified Ground Truth:</strong> AmbitionBox has {len(exact_matches)} reported record(s) for this exact role. Reported range: <strong>₹ {amb_min:.1f} - {amb_max:.1f} LPA</strong> (avg: <strong>₹ {amb_avg:.1f} LPA</strong>) for {rep_exp} experience.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── 7. PRIMARY 3-MODULE TABS ─────────────────────────────────────────────────
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

main_tab1, main_tab2, main_tab3 = st.tabs(
    [
        "📊 Salary & Career Deep Dive",
        "⚖️ Compare Two Offers",
        "🤖 AmbitionBox AI Copilot",
    ]
)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: SALARY & CAREER DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════════════
with main_tab1:
    # ── Section 1: In-Hand Pay Breakdown ──
    st.subheader("💰 Monthly Take-Home & Tax Breakdown")
    st.caption("How your CTC translates to bank credit under the Indian New Tax Regime (Budget 2024 / FY 2024-25 & 2025-26).")

    th_c1, th_c2 = st.columns([1.2, 1.8], gap="large")

    with th_c1:
        # Donut Chart
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
        fig_donut.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with th_c2:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.25rem;">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.5rem 0; color: #64748b;">Annual Cost to Company (CTC)</td>
                        <td style="padding: 0.5rem 0; text-align: right; font-weight: 700; color: #0f172a;">₹ {int(quick_th['ctc']):,}</td>
                        <td style="padding: 0.5rem 0; text-align: right; color: #64748b;">₹ {int(quick_th['ctc']/12):,}/mo</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.5rem 0; color: #64748b;">Estimated Basic (40% of CTC)</td>
                        <td style="padding: 0.5rem 0; text-align: right; font-weight: 600;">₹ {int(quick_th['basic']):,}</td>
                        <td style="padding: 0.5rem 0; text-align: right; color: #64748b;">₹ {int(quick_th['basic']/12):,}/mo</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.5rem 0; color: #dc2626;">(-) Income Tax (New Regime TDS)</td>
                        <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #dc2626;">- ₹ {int(quick_th['tax_annual']):,}</td>
                        <td style="padding: 0.5rem 0; text-align: right; color: #dc2626;">- ₹ {int(quick_th['tax_monthly']):,}/mo</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 0.5rem 0; color: #4338ca;">(-) Employee EPF (Retirement)</td>
                        <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #4338ca;">- ₹ {int(quick_th['epf_annual']):,}</td>
                        <td style="padding: 0.5rem 0; text-align: right; color: #4338ca;">- ₹ {int(quick_th['epf_monthly']):,}/mo</td>
                    </tr>
                    <tr style="border-bottom: 2px solid #e2e8f0;">
                        <td style="padding: 0.5rem 0; color: #d97706;">(-) Professional Tax</td>
                        <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: #d97706;">- ₹ {int(quick_th['pt_annual']):,}</td>
                        <td style="padding: 0.5rem 0; text-align: right; color: #d97706;">- ₹ {int(quick_th['pt_annual']/12):,}/mo</td>
                    </tr>
                    <tr style="background: #f0fdf4;">
                        <td style="padding: 0.75rem 0.5rem; font-weight: 700; color: #047857;">Estimated Net Bank Credit</td>
                        <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 800; font-size: 1.05rem; color: #047857;">₹ {int(quick_th['net_annual']):,}</td>
                        <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 800; font-size: 1.05rem; color: #047857;">₹ {int(quick_th['monthly_in_hand']):,}/mo</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Section 2: 15-Year Career Trajectory ──
    st.subheader(f"📈 15-Year Progression Curve ({selected_company} · {detected_family})")
    st.caption("How compensation expands from early career to staff & principal leadership.")

    exp_steps = [0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0, 12.0, 15.0, 18.0]
    traj_records = []
    for step in exp_steps:
        sub_df = pd.DataFrame(
            [
                {
                    "Company": selected_company,
                    "Job_Title": selected_job,
                    "Industry": industry,
                    "Role_Family": detected_family,
                    "Seniority_Level": detected_seniority,
                    "Rating": rating,
                    "Avg_Exp": step,
                }
            ]
        )
        p_val = round(float(pipeline.predict(sub_df)[0]), 1)
        sub_tree = get_tree_predictions(pipeline, sub_df)
        p10_step = round(float(np.percentile(sub_tree, 10)), 1)
        p90_step = round(float(np.percentile(sub_tree, 90)), 1)
        traj_records.append({"Experience": step, "Salary": p_val, "P10": p10_step, "P90": p90_step})

    traj_df = pd.DataFrame(traj_records)

    fig_traj = go.Figure()
    fig_traj.add_trace(go.Scatter(x=traj_df["Experience"], y=traj_df["P90"], mode="lines", line=dict(width=0), showlegend=False))
    fig_traj.add_trace(go.Scatter(x=traj_df["Experience"], y=traj_df["P10"], mode="lines", line=dict(width=0), fill="tonexty", fillcolor="rgba(79, 70, 229, 0.12)", name="Confidence Corridor (P10 - P90)"))
    fig_traj.add_trace(go.Scatter(x=traj_df["Experience"], y=traj_df["Salary"], mode="lines+markers", line=dict(color="#4f46e5", width=3), name="Estimated Trendline"))
    fig_traj.add_trace(
        go.Scatter(
            x=[selected_exp],
            y=[predicted_salary],
            mode="markers+text",
            marker=dict(size=14, color="#ef4444", symbol="diamond"),
            text=[f"Current: {selected_exp}y (₹{predicted_salary}L)"],
            textposition="top center",
            name="Your Selection",
        )
    )
    fig_traj.update_layout(
        xaxis_title="Years of Experience",
        yaxis_title="Salary (LPA)",
        height=380,
        template="plotly_white",
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_traj, use_container_width=True)

    # Career Milestones
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Fresh Graduate (0-1y)", f"₹ {traj_df.loc[traj_df['Experience'] == 1.0, 'Salary'].values[0]} LPA")
    m_col2.metric("Mid-Level (3-5y)", f"₹ {traj_df.loc[traj_df['Experience'] == 5.0, 'Salary'].values[0]} LPA")
    m_col3.metric("Senior Track (7-9y)", f"₹ {traj_df.loc[traj_df['Experience'] == 9.0, 'Salary'].values[0]} LPA")
    m_col4.metric("Lead / Principal (12y+)", f"₹ {traj_df.loc[traj_df['Experience'] == 15.0, 'Salary'].values[0]} LPA")

    st.markdown("---")

    # ── Section 3: Peer Scatter Plot & Comparable Records ──
    st.subheader(f"🔍 Market Benchmarks: {detected_family}")
    st.caption("How your estimate compares against peers across all employers in the dataset.")

    fam_records = df[df["Role_Family"] == detected_family].copy()
    if len(fam_records) > 0:
        fig_scatter = px.scatter(
            fam_records,
            x="Avg_Exp",
            y="Avg_Salary_LPA",
            color="Company",
            opacity=0.7,
            title=f"Compensation vs Experience across Companies ({detected_family})",
            labels={"Avg_Exp": "Experience (Years)", "Avg_Salary_LPA": "Salary (LPA)"},
            hover_data=["Company", "Job_Title", "Min_Salary_LPA", "Max_Salary_LPA"],
        )
        fig_scatter.add_trace(
            go.Scatter(
                x=[selected_exp],
                y=[predicted_salary],
                mode="markers+text",
                marker=dict(size=16, color="#ef4444", symbol="star", line=dict(width=2, color="white")),
                text=["Your Estimate"],
                textposition="top center",
                name="Your Selection",
            )
        )
        fig_scatter.update_layout(height=400, template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Top comparable table
    comparable_df = find_comparable_records(df, selected_company, selected_job, detected_family, selected_exp, n=8)
    show_cols = ["Company", "Job_Title", "Role_Family", "Avg_Exp", "Min_Salary_LPA", "Max_Salary_LPA", "Avg_Salary_LPA"]
    clean_comp = comparable_df[show_cols].copy()
    clean_comp.columns = ["Company", "Role", "Domain", "Exp (Yrs)", "Min (LPA)", "Max (LPA)", "Avg (LPA)"]
    clean_comp = clean_comp.reset_index(drop=True)
    clean_comp.index = clean_comp.index + 1

    st.markdown("**Top 8 Most Relevant Benchmark Records:**")
    st.dataframe(clean_comp, use_container_width=True)

    st.markdown("---")

    # ── Section 4: Employee Culture Voice (Likes & Dislikes) ──
    top_likes = comp_info.get("top_likes", [])
    top_dislikes = comp_info.get("top_dislikes", [])
    if top_likes or top_dislikes:
        st.subheader(f"🗣️ Verified Employee Voice: {selected_company}")
        st.caption("Extracted from 43,000+ AmbitionBox employee reviews.")

        voice_col1, voice_col2 = st.columns(2, gap="large")
        with voice_col1:
            st.markdown("#### 👍 What Employees Appreciate")
            for lk in top_likes:
                st.markdown(f'<div class="pros-quote">"{lk.strip()}"</div>', unsafe_allow_html=True)

        with voice_col2:
            st.markdown("#### 👎 Critical Friction Points & Cons")
            for dl in top_dislikes:
                st.markdown(f'<div class="cons-quote">"{dl.strip()}"</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: OFFER & COMPANY COMPARE
# ═══════════════════════════════════════════════════════════════════════════════
with main_tab2:
    st.subheader("⚖️ Head-to-Head Offer & Employer Benchmark")
    st.caption("Compare compensation, net in-hand take-home delta, and culture ratings between two employers.")

    with st.container(border=True):
        cmp_c1, cmp_c2, cmp_c3 = st.columns([1.5, 1.5, 1.2], gap="medium")

        with cmp_c1:
            comp_a = st.selectbox("Company A", companies, index=companies.index(selected_company), key="cmp_a")
            jobs_a = company_jobs.get(comp_a, all_job_titles)
            default_a_idx = jobs_a.index(selected_job) if selected_job in jobs_a else 0
            job_a = st.selectbox("Role at A", jobs_a, index=default_a_idx, key="role_a")

        with cmp_c2:
            other_default = "Accenture" if "Accenture" in companies and comp_a != "Accenture" else (companies[1] if len(companies) > 1 else companies[0])
            comp_b = st.selectbox("Company B", companies, index=companies.index(other_default), key="cmp_b")
            jobs_b = company_jobs.get(comp_b, all_job_titles)
            default_b_idx = jobs_b.index(selected_job) if selected_job in jobs_b else 0
            job_b = st.selectbox("Role at B", jobs_b, index=default_b_idx, key="role_b")

        with cmp_c3:
            cmp_exp = st.slider("Shared Experience", 0.0, experience_cap, selected_exp, step=0.5, key="cmp_exp")

    # Evaluate Company A
    info_a = company_insights.get(comp_a, {})
    ind_a = info_a.get("industry", "Corporate")
    rat_a = float(info_a.get("rating", 3.5))
    fam_a, sen_a = categorize_job(job_a)
    df_a = pd.DataFrame([{"Company": comp_a, "Job_Title": job_a, "Industry": ind_a, "Role_Family": fam_a, "Seniority_Level": sen_a, "Rating": rat_a, "Avg_Exp": cmp_exp}])
    pred_a = round(float(pipeline.predict(df_a)[0]), 1)
    th_a = calculate_take_home(pred_a)

    # Evaluate Company B
    info_b = company_insights.get(comp_b, {})
    ind_b = info_b.get("industry", "Corporate")
    rat_b = float(info_b.get("rating", 3.5))
    fam_b, sen_b = categorize_job(job_b)
    df_b = pd.DataFrame([{"Company": comp_b, "Job_Title": job_b, "Industry": ind_b, "Role_Family": fam_b, "Seniority_Level": sen_b, "Rating": rat_b, "Avg_Exp": cmp_exp}])
    pred_b = round(float(pipeline.predict(df_b)[0]), 1)
    th_b = calculate_take_home(pred_b)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Comparison Metric Cards
    res_a, res_b, res_delta = st.columns([1.2, 1.2, 1.4], gap="medium")
    with res_a:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-caption">{comp_a}</div>
                <div style="font-size: 2rem; font-weight:800; color:#0f172a;">₹ {pred_a} LPA</div>
                <div style="color: #047857; font-weight:700; font-size:1.05rem;">₹ {int(th_a['monthly_in_hand']):,}/mo in-hand</div>
                <div class="metric-sub">⭐ {rat_a} / 5.0 Rating · {info_a.get('reviews', 'N/A')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with res_b:
        diff_ctc = round(pred_b - pred_a, 1)
        diff_pct = round((diff_ctc / pred_a) * 100, 1) if pred_a > 0 else 0
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-caption">{comp_b}</div>
                <div style="font-size: 2rem; font-weight:800; color:#0f172a;">₹ {pred_b} LPA</div>
                <div style="color: #047857; font-weight:700; font-size:1.05rem;">₹ {int(th_b['monthly_in_hand']):,}/mo in-hand</div>
                <div class="metric-sub">⭐ {rat_b} / 5.0 Rating · {info_b.get('reviews', 'N/A')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with res_delta:
        diff_inhand = int(th_b["monthly_in_hand"] - th_a["monthly_in_hand"])
        delta_color = "#047857" if diff_inhand >= 0 else "#dc2626"
        st.markdown(
            f"""
            <div class="metric-box-highlight">
                <div class="metric-caption">Head-to-Head Delta</div>
                <div style="font-size: 1.8rem; font-weight:800; color: {delta_color};">
                    {diff_inhand:+,} / mo
                </div>
                <div style="font-weight: 700; color: #0f172a; margin-top: 0.2rem;">
                    CTC Gap: {diff_ctc:+} LPA ({diff_pct:+}% vs A)
                </div>
                <div class="metric-sub">Annual Take-Home Difference: ₹ {abs(diff_inhand*12):,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Bar Chart Comparison
    fig_cmp = go.Figure(
        data=[
            go.Bar(name="Annual CTC (LPA)", x=[comp_a, comp_b], y=[pred_a, pred_b], marker_color=["#4f46e5", "#06b6d4"]),
            go.Bar(name="Annual Net In-Hand (LPA)", x=[comp_a, comp_b], y=[round(th_a["net_annual"]/100000, 1), round(th_b["net_annual"]/100000, 1)], marker_color=["#10b981", "#34d399"]),
        ]
    )
    fig_cmp.update_layout(barmode="group", height=350, template="plotly_white", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_cmp, use_container_width=True)

    # Side-by-Side Culture Comparison
    st.markdown("#### 🏢 Culture & Sentiment Head-to-Head")
    side_a, side_b = st.columns(2, gap="large")
    with side_a:
        st.markdown(f"**{comp_a}** ({ind_a} · HQ: {info_a.get('hq_city', 'India')})")
        if info_a.get("top_likes"):
            st.markdown(f'<div class="pros-quote">"{info_a["top_likes"][0]}"</div>', unsafe_allow_html=True)
        if info_a.get("top_dislikes"):
            st.markdown(f'<div class="cons-quote">"{info_a["top_dislikes"][0]}"</div>', unsafe_allow_html=True)

    with side_b:
        st.markdown(f"**{comp_b}** ({ind_b} · HQ: {info_b.get('hq_city', 'India')})")
        if info_b.get("top_likes"):
            st.markdown(f'<div class="pros-quote">"{info_b["top_likes"][0]}"</div>', unsafe_allow_html=True)
        if info_b.get("top_dislikes"):
            st.markdown(f'<div class="cons-quote">"{info_b["top_dislikes"][0]}"</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: AMBITIONBOX AI REVIEW COPILOT
# ═══════════════════════════════════════════════════════════════════════════════
with main_tab3:
    st.subheader("🤖 AmbitionBox AI Copilot: Workplace Culture Intelligence")
    st.caption("Ask natural language questions across 33,200+ review vectors embedded from verified AmbitionBox employee feedback.")

    with st.container(border=True):
        sc_col1, sc_col2 = st.columns([2, 1], gap="medium")
        with sc_col1:
            scope_mode = st.radio(
                "Search Target",
                [f"Filter by selected employer ({selected_company})", "Search across all 118 employers"],
                horizontal=True,
            )
        with sc_col2:
            top_k_rev = st.slider("Citations to Analyze", 3, 8, 5)

        target_employer = selected_company if "Filter by selected employer" in scope_mode else None

        # Quick question pills
        st.markdown("**💡 Popular Topics (click to ask):**")
        pill_row1, pill_row2, pill_row3, pill_row4 = st.columns(4)
        preset_q = None
        target_label = target_employer or selected_company

        if pill_row1.button("⚖️ Work-Life Balance", use_container_width=True):
            preset_q = f"How is the work life balance, overtime pressure, and manager expectations at {target_label}?"
        if pill_row2.button("📈 Appraisals & Increments", use_container_width=True):
            preset_q = f"How are annual appraisals, salary hikes, and promotion policies at {target_label}?"
        if pill_row3.button("🎓 Freshers & Growth", use_container_width=True):
            preset_q = f"Is {target_label} good for freshers, learning tech stacks, and career growth?"
        if pill_row4.button("🏢 Job Security & Bench", use_container_width=True):
            preset_q = f"What is the job security, bench policy, and layoff situation at {target_label}?"

        ai_query = st.text_input(
            "Ask about company culture, compensation sentiment, or management:",
            value=preset_q if preset_q else f"How is the work-life balance and culture at {target_label}?",
            placeholder="e.g. Do developers get good increments? Is client-side micromanagement common?",
        )

        trigger_search = st.button("Analyze Reviews 🚀", type="primary", use_container_width=True)

    # API key check from Streamlit Cloud secrets or environment
    cloud_secret = ""
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            cloud_secret = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    active_api_key = cloud_secret or os.getenv("GEMINI_API_KEY", "")

    if trigger_search:
        with st.spinner("Searching 33,200+ review vectors and synthesizing insights..."):
            try:
                import rag_assistant

                retrieved = rag_assistant.retrieve_reviews(ai_query, company=target_employer, k=top_k_rev)
                result = rag_assistant.synthesize_answer(ai_query, retrieved, api_key=active_api_key)

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                # Sentiment Header Strip
                stat1, stat2, stat3 = st.columns(3)
                stat1.metric("Verified Reviews Retrieved", len(retrieved))
                stat2.metric("Average Employee Rating", f"⭐ {result.get('avg_rating', 3.5)} / 5.0")
                engine_title = "Google Gemini AI" if result.get("source") == "gemini" else "Local Semantic Vector Search (FAISS)"
                stat3.metric("Synthesis Engine", engine_title)

                # Executive Answer Box
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 1.25rem 1.5rem; margin: 1rem 0;">
                        {result['text']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Verified Source Citations
                st.markdown("#### 🔍 Source Citations & Review Snippets")
                for i, rv in enumerate(retrieved, 1):
                    with st.expander(f"Review #{i} — {rv['company']} · {rv['job']} in {rv['location']} (Rating: ⭐ {rv['rating']})"):
                        c_pro, c_con = st.columns(2)
                        with c_pro:
                            st.markdown("##### 👍 Likes / Pros")
                            st.write(rv["likes"] if rv["likes"] else "No specific likes recorded.")
                        with c_con:
                            st.markdown("##### 👎 Dislikes / Cons")
                            st.write(rv["dislikes"] if rv["dislikes"] else "No specific dislikes recorded.")

            except Exception as e:
                st.error(f"Error executing review search: {e}")


# ── 8. FOOTER & DATA METHODOLOGY ─────────────────────────────────────────────
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

with st.expander("ℹ️ Data Provenance, Machine Learning Methodology & Disclaimers"):
    st.markdown(
        f"""
### 📊 Dataset Origin
- **Source:** Compensation and review data scraped from [AmbitionBox](https://www.ambitionbox.com/salaries) in mid-2026.
- **Coverage:** **{len(companies)} companies** and **{len(all_job_titles)} unique job titles**.
- **Role Taxonomy:** Parsed into **{len(role_families)} Canonical Role Families** and **5 Seniority Levels** via rule-based NLP.
- **Employee Reviews & RAG Index:** **33,200+ review vectors** embedded via `all-MiniLM-L6-v2` and indexed with FAISS for semantic review retrieval.

### 🤖 Machine Learning Architecture (Voting Ensemble)
- **Architecture:** `sklearn.pipeline.Pipeline` with `ColumnTransformer` + `VotingRegressor`:
  - **Estimator 1:** `RandomForestRegressor` (400 trees, max depth 22).
  - **Estimator 2:** `HistGradientBoostingRegressor` (200 iterations, 31 max leaves).
- **Holdout Evaluation Metrics:**
  - **R² Score:** `{metadata.get('r2_score', 'N/A')}` *(0.5655)*
  - **Mean Absolute Error (MAE):** `{metadata.get('mae_lpa', 'N/A')} LPA` *(₹3.85 Lakhs)*
  - **Root Mean Squared Error (RMSE):** `{metadata.get('rmse_lpa', 'N/A')} LPA` *(₹5.78 Lakhs)*

### ⚠️ Disclaimers
AmbitionBox records are self-reported by job seekers and employees. Actual compensation depends on performance bonuses, RSUs/ESOPs, academic tier, specific technology stacks, and negotiation skill. Use this platform as a strategic compass for salary negotiations and market benchmarking.
"""
    )

st.markdown(
    '<p style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 1.5rem;">Built with Streamlit & Plotly · Voting Ensemble ML · Sourced from AmbitionBox</p>',
    unsafe_allow_html=True,
)
