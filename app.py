"""
app.py -- India Salary & Career Intelligence Platform.

Powered by real salary and review data scraped from AmbitionBox.
Features:
- Voting Ensemble ML (Random Forest + HistGradientBoosting) with NLP Role Normalization
- Confidence intervals derived from 400 ensemble trees
- RAG (Retrieval-Augmented Generation) AI assistant over 33,200+ indexed employee reviews
- Company intelligence cards (rating, reviews, industry, HQ city)
- Real employee voice (likes & dislikes from AmbitionBox reviews)
- In-Hand / Take-Home Salary Calculator (India New Tax Regime)
- Company vs Company Offer Comparison
- Career progression trajectory simulation (0 to 18 years)
- Interactive Plotly visualizations
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

# ── 1. PAGE SETUP ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Salary & Career Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
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


# ── 3. NLP HELPER FUNCTIONS ──────────────────────────────────────────────────
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


# ── 4. SIDEBAR CONTROLS ──────────────────────────────────────────────────────
with st.sidebar:
    st.title("💼 Intelligence Hub")
    st.markdown("Explore Indian corporate compensation backed by **real AmbitionBox data**.")
    st.divider()

    selected_company = st.selectbox(
        "🏢 Select Company",
        companies,
        index=companies.index("TCS") if "TCS" in companies else 0,
    )

    # Job selection mode
    job_mode = st.radio(
        "Browse Roles By",
        ["Roles scraped at this company", "Search all 750+ roles", "Filter by Role Family"],
        horizontal=False,
    )

    if job_mode == "Roles scraped at this company":
        available_jobs = company_jobs.get(selected_company, all_job_titles)
        if not available_jobs:
            available_jobs = all_job_titles
        selected_job = st.selectbox("👤 Job Role", available_jobs)
    elif job_mode == "Filter by Role Family":
        chosen_family = st.selectbox("📂 Role Family", role_families)
        family_jobs = df[df["Role_Family"] == chosen_family]["Job_Title"].unique().tolist()
        if not family_jobs:
            family_jobs = all_job_titles
        selected_job = st.selectbox("👤 Job Role", sorted(family_jobs))
    else:
        selected_job = st.selectbox("👤 Job Role", all_job_titles)

    # Auto-detect Role Family & Seniority via NLP
    detected_family, detected_seniority = categorize_job(selected_job)

    st.markdown(
        f"🏷️ **Detected Domain:** `{detected_family}`  \n"
        f"🎖️ **Level:** `{detected_seniority}`"
    )

    selected_exp = st.slider(
        "📅 Experience (Years)",
        min_value=0.0,
        max_value=experience_cap,
        value=min(4.0, experience_cap),
        step=0.5,
    )

    st.divider()
    st.markdown("### 🤖 AI Review Assistant")
    cloud_secret = ""
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            cloud_secret = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    gemini_api_key = st.text_input(
        "Google Gemini API Key (Optional)",
        type="password",
        value=cloud_secret or os.getenv("GEMINI_API_KEY", ""),
        help="Optional: Powers conversational AI synthesis. If left empty, the RAG engine uses local semantic search with zero API calls!",
    )

    st.divider()
    st.markdown("### 📊 Dataset Pulse")
    col_sb1, col_sb2 = st.columns(2)
    col_sb1.metric("Companies", len(companies))
    col_sb2.metric("Job Roles", len(all_job_titles))
    st.caption("Model: Voting Ensemble (RF + HGB) · 33,200+ FAISS reviews")


# ── 5. LOOKUP COMPANY METADATA & PREDICT ──────────────────────────────────────
comp_info = company_insights.get(selected_company, {})
industry = comp_info.get("industry", "Corporate")
rating = float(comp_info.get("rating", 3.5))
hq_city = comp_info.get("hq_city", "India")
reviews_count = comp_info.get("reviews", "10k+")
median_sal = comp_info.get("median_salary", "N/A")

# Prepare input DataFrame for Voting Ensemble
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

# Run prediction
predicted_salary = round(float(pipeline.predict(user_input_df)[0]), 1)
tree_predictions = get_tree_predictions(pipeline, user_input_df)
p10 = round(float(np.percentile(tree_predictions, 10)), 1)
p90 = round(float(np.percentile(tree_predictions, 90)), 1)
std_dev = round(float(np.std(tree_predictions)), 1)

# Exact match check in scraped records
exact_matches = df[(df["Company"] == selected_company) & (df["Job_Title"] == selected_job)]


# ── 6. MAIN CONTENT AREA & TABS ──────────────────────────────────────────────
st.title("🇮🇳 India Salary & Career Intelligence")
st.markdown(
    f"Estimate salaries, chat with 43,000+ employee reviews, compare company packages, and simulate take-home pay based on **real AmbitionBox data**."
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🎯 Salary Prediction",
        "🤖 Ask AmbitionBox AI",
        "⚖️ Offer & Company Compare",
        "💰 In-Hand Pay Calculator",
        "📈 Career Progression",
        "ℹ️ Data & Methodology",
    ]
)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: SALARY PREDICTION & INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    # ── Company Badge Card ──
    with st.container():
        c_card1, c_card2, c_card3, c_card4, c_card5 = st.columns(5)
        c_card1.metric("🏢 Company", selected_company)
        c_card2.metric("⭐ Rating", f"{rating} / 5.0")
        c_card3.metric("💬 Total Reviews", reviews_count)
        c_card4.metric("🏭 Industry", industry)
        c_card5.metric("📍 HQ", hq_city)

    st.markdown("---")

    # ── Prediction Highlights ──
    st.subheader(f"Predicted Compensation: {selected_job}")
    st.caption(
        f"Domain: **{detected_family}** · Level: **{detected_seniority}** · "
        f"At **{selected_company}** with **{selected_exp} yrs** experience"
    )

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Ensemble Prediction", f"₹ {predicted_salary} LPA")
    m_col2.metric("Likely Range (P10 - P90)", f"₹ {p10} - {p90} LPA")
    m_col3.metric("Tree Disagreement", f"± {std_dev} LPA")

    # Quick In-Hand teaser
    quick_th = calculate_take_home(predicted_salary)
    m_col4.metric(
        "Est. Monthly In-Hand",
        f"₹ {int(quick_th['monthly_in_hand']):,}",
        help="Calculated under New Tax Regime FY 2024-25 / FY 2025-26 with ₹75k standard deduction",
    )

    # ── Ground Truth Banner ──
    if len(exact_matches) > 0:
        amb_min = exact_matches["Min_Salary_LPA"].min()
        amb_max = exact_matches["Max_Salary_LPA"].max()
        amb_avg = exact_matches["Avg_Salary_LPA"].mean()
        reported_exp = exact_matches["Experience"].iloc[0]
        st.success(
            f"✅ **AmbitionBox Ground Truth:** {len(exact_matches)} exact match record(s) scraped for this role! "
            f"Reported Range: **₹ {amb_min:.1f} - {amb_max:.1f} LPA** (Mean: **₹ {amb_avg:.1f} LPA**) for {reported_exp} experience."
        )
    else:
        st.info(
            f"ℹ️ **Ensemble Generalization:** No exact record for '{selected_job}' specifically at {selected_company} in the scrape. "
            f"The model estimated this using market data for **{detected_family}** ({detected_seniority}), {selected_company}'s industry ({industry}), and company rating ({rating}).",
            icon="ℹ️",
        )

    # ── Employee Sentiment (Likes & Dislikes) ──
    top_likes = comp_info.get("top_likes", [])
    top_dislikes = comp_info.get("top_dislikes", [])
    if top_likes or top_dislikes:
        with st.expander(f"🗣️ Employee Voice & Culture at {selected_company} (from AmbitionBox Reviews)", expanded=False):
            sent_col1, sent_col2 = st.columns(2)
            with sent_col1:
                st.markdown("#### 👍 What Employees Like")
                if top_likes:
                    for lk in top_likes:
                        st.markdown(f"- *\"{lk.strip()}\"*")
                else:
                    st.caption("No specific likes captured in sample.")
            with sent_col2:
                st.markdown("#### 👎 What Employees Dislike")
                if top_dislikes:
                    for dl in top_dislikes:
                        st.markdown(f"- *\"{dl.strip()}\"*")
                else:
                    st.caption("No specific dislikes captured in sample.")

    st.markdown("---")

    # ── Sub-tabs for deep visual exploration ──
    vtab1, vtab2, vtab3 = st.tabs(
        ["📈 Salary vs Experience Curve", "🔍 Comparable Salaries", "📊 Company Distribution"]
    )

    with vtab1:
        # Cross-company comparison for same role family
        family_records = df[df["Role_Family"] == detected_family].copy()
        if len(family_records) > 0:
            fig_scatter = px.scatter(
                family_records,
                x="Avg_Exp",
                y="Avg_Salary_LPA",
                color="Company",
                opacity=0.7,
                size_max=12,
                title=f"Compensation vs Experience in {detected_family} across Companies",
                labels={"Avg_Exp": "Experience (Years)", "Avg_Salary_LPA": "Salary (LPA)"},
                hover_data=["Company", "Job_Title", "Min_Salary_LPA", "Max_Salary_LPA"],
            )

            # User prediction star marker
            fig_scatter.add_trace(
                go.Scatter(
                    x=[selected_exp],
                    y=[predicted_salary],
                    mode="markers+text",
                    marker=dict(size=18, color="red", symbol="star", line=dict(width=2, color="white")),
                    text=["Your Estimate"],
                    textposition="top center",
                    name="Your Prediction",
                )
            )

            # P10 - P90 confidence shaded rectangle
            fig_scatter.add_hrect(
                y0=p10,
                y1=p90,
                fillcolor="red",
                opacity=0.08,
                line_width=0,
                annotation_text="Likely range",
                annotation_position="top left",
            )
            fig_scatter.update_layout(height=450, template="plotly_white")
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info(f"Few records found for {detected_family}.")

    with vtab2:
        comparable_df = find_comparable_records(df, selected_company, selected_job, detected_family, selected_exp, n=10)
        show_cols = ["Company", "Job_Title", "Role_Family", "Avg_Exp", "Min_Salary_LPA", "Max_Salary_LPA", "Avg_Salary_LPA"]
        clean_comp = comparable_df[show_cols].copy()
        clean_comp.columns = ["Company", "Role", "Domain", "Exp (Yrs)", "Min (LPA)", "Max (LPA)", "Avg (LPA)"]
        clean_comp = clean_comp.reset_index(drop=True)
        clean_comp.index = clean_comp.index + 1

        st.markdown(f"**Top {len(clean_comp)} most relevant data points** matching role family, company, and experience:")
        st.dataframe(clean_comp, use_container_width=True)

        avg_comp_val = round(clean_comp["Avg (LPA)"].mean(), 1)
        st.caption(f"Average among comparable roles: **₹ {avg_comp_val} LPA** | Your Model Prediction: **₹ {predicted_salary} LPA**")

    with vtab3:
        comp_records = df[df["Company"] == selected_company]
        if len(comp_records) > 0:
            fig_hist = px.histogram(
                comp_records,
                x="Avg_Salary_LPA",
                nbins=20,
                title=f"Reported Salary Distribution at {selected_company} ({len(comp_records)} records)",
                labels={"Avg_Salary_LPA": "Salary (LPA)", "count": "Count"},
                color_discrete_sequence=["#1f77b4"],
                opacity=0.8,
            )
            fig_hist.add_vline(
                x=predicted_salary,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Estimate: ₹ {predicted_salary} LPA",
                annotation_position="top right",
            )
            fig_hist.update_layout(height=400, template="plotly_white")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info(f"No records available for {selected_company}.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: ASK AMBITIONBOX AI (RAG REVIEW ASSISTANT)
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🤖 Ask AmbitionBox AI: Culture & Employee Review Assistant")
    st.caption(
        "Semantic search & RAG synthesis across **33,200+ indexed review vectors** from real verified employees."
    )

    scope_col1, scope_col2, scope_col3 = st.columns([2, 1, 1])
    with scope_col1:
        search_scope = st.radio(
            "Search Scope",
            [f"Filter by active company ({selected_company})", "Search across all 100+ companies"],
            horizontal=True,
            key="rag_scope",
        )
    with scope_col2:
        top_k = st.slider("Reviews to Analyze", min_value=3, max_value=8, value=5, key="rag_topk")
    with scope_col3:
        filter_comp = selected_company if "Filter by active company" in search_scope else None
        st.markdown(f"**Target Company:**  \n`{filter_comp or 'All Companies'}`")

    # Quick prompt pills
    st.markdown("**💡 Quick Questions:**")
    pill_c1, pill_c2, pill_c3, pill_c4 = st.columns(4)
    q_preset = None
    target_name = filter_comp or selected_company

    if pill_c1.button("⚖️ Work-Life Balance", use_container_width=True):
        q_preset = f"How is the work life balance, overtime expectations, and manager pressure at {target_name}?"
    if pill_c2.button("📈 Appraisals & Salary Hikes", use_container_width=True):
        q_preset = f"How are the yearly appraisals, salary hikes, and promotion policies at {target_name}?"
    if pill_c3.button("🎓 Freshers & Learning", use_container_width=True):
        q_preset = f"Is {target_name} good for freshers, learning technologies, and career growth?"
    if pill_c4.button("🏢 Job Security & Bench", use_container_width=True):
        q_preset = f"What is the job security, bench policy, and layoff situation at {target_name}?"

    user_query = st.text_input(
        "Ask anything about employee experiences:",
        value=q_preset if q_preset else f"How is the work-life balance and culture at {target_name}?",
        placeholder="e.g. Do developers get good increments? Is client side micromanagement common?",
        key="rag_query_input",
    )

    if st.button("Analyze Employee Reviews 🚀", type="primary", use_container_width=True, key="run_rag_btn"):
        with st.spinner("Searching 33,200+ review vectors and synthesizing insights..."):
            try:
                import rag_assistant

                retrieved = rag_assistant.retrieve_reviews(user_query, company=filter_comp, k=top_k)
                result = rag_assistant.synthesize_answer(user_query, retrieved, api_key=gemini_api_key)

                st.markdown("---")

                # Metrics summary row
                b_col1, b_col2, b_col3 = st.columns(3)
                b_col1.metric("Verified Reviews Retrieved", len(retrieved))
                b_col2.metric("Average Employee Rating", f"⭐ {result.get('avg_rating', 3.5)} / 5.0")
                engine_name = "Google Gemini AI" if result.get("source") == "gemini" else "Local Semantic Vector Search (FAISS)"
                b_col3.metric("Analysis Engine", engine_name)

                # Synthesis Output
                st.markdown("### 📝 Executive Review Synthesis")
                st.markdown(result["text"])

                # Source Citations
                st.markdown("---")
                st.markdown(f"### 🔍 Retrieved Source Reviews ({len(retrieved)} Citations)")
                for idx, rev in enumerate(retrieved, 1):
                    with st.expander(
                        f"Review #{idx} — {rev['company']} · {rev['job']} in {rev['location']} (Rating: ⭐ {rev['rating']})"
                    ):
                        rev_c1, rev_c2 = st.columns(2)
                        with rev_c1:
                            st.markdown("##### 👍 Likes / Pros")
                            st.write(rev["likes"] if rev["likes"] else "No specific likes recorded.")
                        with rev_c2:
                            st.markdown("##### 👎 Dislikes / Cons")
                            st.write(rev["dislikes"] if rev["dislikes"] else "No specific dislikes recorded.")

            except Exception as e:
                st.error(f"Error during review retrieval: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: COMPANY VS COMPANY BENCHMARK
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("⚖️ Compare Two Offers or Target Companies")
    st.caption("Direct side-by-side benchmark for compensation, culture, and ratings.")

    cmp_c1, cmp_c2 = st.columns(2)
    with cmp_c1:
        st.markdown("### Company A")
        comp_a = st.selectbox("Company A", companies, index=companies.index(selected_company), key="cmp_a")
        jobs_a = company_jobs.get(comp_a, all_job_titles)
        default_job_a_idx = jobs_a.index(selected_job) if selected_job in jobs_a else 0
        job_a = st.selectbox("Role at Company A", jobs_a, index=default_job_a_idx, key="role_a")

    with cmp_c2:
        st.markdown("### Company B")
        other_default = "Accenture" if "Accenture" in companies and comp_a != "Accenture" else (companies[1] if len(companies) > 1 else companies[0])
        comp_b = st.selectbox("Company B", companies, index=companies.index(other_default), key="cmp_b")
        jobs_b = company_jobs.get(comp_b, all_job_titles)
        default_job_b_idx = jobs_b.index(selected_job) if selected_job in jobs_b else 0
        job_b = st.selectbox("Role at Company B", jobs_b, index=default_job_b_idx, key="role_b")

    cmp_exp = st.slider("Shared Experience Level (Years)", 0.0, experience_cap, selected_exp, step=0.5, key="cmp_exp_slider")

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

    st.markdown("---")

    # Metrics comparison row
    r_col1, r_col2, r_col3 = st.columns([2, 2, 2])
    with r_col1:
        st.metric(f"{comp_a} Predicted CTC", f"₹ {pred_a} LPA")
        st.caption(f"Domain: **{fam_a}** · Net Take-Home: **₹ {int(th_a['monthly_in_hand']):,}/mo**")
    with r_col2:
        diff_val = round(pred_b - pred_a, 1)
        diff_pct = round((diff_val / pred_a) * 100, 1) if pred_a > 0 else 0
        st.metric(f"{comp_b} Predicted CTC", f"₹ {pred_b} LPA", delta=f"{diff_val:+} LPA ({diff_pct:+}% vs A)")
        st.caption(f"Domain: **{fam_b}** · Net Take-Home: **₹ {int(th_b['monthly_in_hand']):,}/mo**")
    with r_col3:
        monthly_diff = int(th_b["monthly_in_hand"] - th_a["monthly_in_hand"])
        st.metric("Net Monthly In-Hand Delta", f"₹ {abs(monthly_diff):,}", delta=f"{monthly_diff:+} / month")

    # Visual side-by-side bar chart
    fig_cmp = go.Figure(
        data=[
            go.Bar(name="Predicted Annual CTC (LPA)", x=[comp_a, comp_b], y=[pred_a, pred_b], marker_color=["#1f77b4", "#2ca02c"]),
            go.Bar(name="Est. Annual Take-Home (LPA)", x=[comp_a, comp_b], y=[round(th_a["net_annual"]/100000, 1), round(th_b["net_annual"]/100000, 1)], marker_color=["#aec7e8", "#98df8a"]),
        ]
    )
    fig_cmp.update_layout(barmode="group", height=380, title="Compensation Comparison (CTC vs In-Hand)", template="plotly_white")
    st.plotly_chart(fig_cmp, use_container_width=True)

    # Ratings & Culture Side-by-Side
    st.markdown("### 🏢 Culture & Brand Comparison")
    card_a, card_b = st.columns(2)
    with card_a:
        st.markdown(f"#### {comp_a}")
        st.markdown(f"⭐ **AmbitionBox Rating:** {rat_a} / 5.0  \n💬 **Total Reviews:** {info_a.get('reviews', 'N/A')}  \n🏭 **Industry:** {ind_a}  \n📍 **HQ:** {info_a.get('hq_city', 'India')}")
        if info_a.get("top_likes"):
            st.markdown(f"**👍 Top Pro:** *\"{info_a['top_likes'][0]}\"*")
        if info_a.get("top_dislikes"):
            st.markdown(f"**👎 Top Con:** *\"{info_a['top_dislikes'][0]}\"*")

    with card_b:
        st.markdown(f"#### {comp_b}")
        st.markdown(f"⭐ **AmbitionBox Rating:** {rat_b} / 5.0  \n💬 **Total Reviews:** {info_b.get('reviews', 'N/A')}  \n🏭 **Industry:** {ind_b}  \n📍 **HQ:** {info_b.get('hq_city', 'India')}")
        if info_b.get("top_likes"):
            st.markdown(f"**👍 Top Pro:** *\"{info_b['top_likes'][0]}\"*")
        if info_b.get("top_dislikes"):
            st.markdown(f"**👎 Top Con:** *\"{info_b['top_dislikes'][0]}\"*")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: IN-HAND PAY & TAX CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("💰 In-Hand / Take-Home Salary Calculator")
    st.caption("Calculate actual monthly bank credit based on the Indian New Tax Regime (Budget 2024 / FY 2024-25 & 2025-26).")

    calc_col1, calc_col2 = st.columns([1, 2])
    with calc_col1:
        calc_ctc = st.number_input("Annual CTC (in ₹ Lakhs)", min_value=1.0, max_value=100.0, value=float(predicted_salary), step=0.5)
        st.markdown("""
        **Tax Regime Rules Applied:**
        - **Standard Deduction:** ₹75,000
        - **Tax-Free Income u/s 87A:** Nil tax up to ₹7.75 Lakhs CTC
        - **Slabs:** 3-7L: 5%, 7-10L: 10%, 10-12L: 15%, 12-15L: 20%, >15L: 30%
        - **EPF Contribution:** 12% of basic (~40% CTC)
        - **Professional Tax:** ₹2,400/yr standard
        """)

    th_res = calculate_take_home(calc_ctc)

    with calc_col2:
        res_c1, res_c2 = st.columns(2)
        res_c1.metric("Estimated Monthly In-Hand", f"₹ {int(th_res['monthly_in_hand']):,}")
        res_c2.metric("Annual In-Hand (Net Pay)", f"₹ {int(th_res['net_annual']):,}")

        # Breakdown Donut Chart
        breakdown_labels = ["Net Take-Home Pay", "Income Tax (TDS)", "EPF (Retirement Fund)", "Professional Tax"]
        breakdown_values = [
            th_res["net_annual"],
            th_res["tax_annual"],
            th_res["epf_annual"] * 2,  # both employee + employer
            th_res["pt_annual"],
        ]
        fig_donut = go.Figure(data=[go.Pie(labels=breakdown_labels, values=breakdown_values, hole=0.5, marker=dict(colors=["#2ca02c", "#d62728", "#1f77b4", "#ff7f0e"]))])
        fig_donut.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20), title=f"Annual CTC Breakdown (₹ {calc_ctc:.1f} Lakhs)")
        st.plotly_chart(fig_donut, use_container_width=True)

    # Detailed Table
    st.markdown("#### 📑 Monthly & Annual Breakdown")
    breakdown_table = pd.DataFrame(
        [
            {"Component": "Cost to Company (CTC)", "Annual (₹)": f"₹ {int(th_res['ctc']):,}", "Monthly (₹)": f"₹ {int(th_res['ctc']/12):,}"},
            {"Component": "Basic Salary (Est. 40%)", "Annual (₹)": f"₹ {int(th_res['basic']):,}", "Monthly (₹)": f"₹ {int(th_res['basic']/12):,}"},
            {"Component": "Employee EPF Deduction", "Annual (₹)": f"₹ {int(th_res['epf_annual']):,}", "Monthly (₹)": f"₹ {int(th_res['epf_monthly']):,}"},
            {"Component": "Estimated Income Tax (New Regime)", "Annual (₹)": f"₹ {int(th_res['tax_annual']):,}", "Monthly (₹)": f"₹ {int(th_res['tax_annual']/12):,}"},
            {"Component": "Professional Tax", "Annual (₹)": f"₹ {int(th_res['pt_annual']):,}", "Monthly (₹)": f"₹ {int(th_res['pt_annual']/12):,}"},
            {"Component": "Estimated Take-Home In-Hand", "Annual (₹)": f"₹ {int(th_res['net_annual']):,}", "Monthly (₹)": f"₹ {int(th_res['monthly_in_hand']):,}"},
        ]
    )
    st.table(breakdown_table)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: CAREER PROGRESSION TRAJECTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader(f"📈 15-Year Career Trajectory: {selected_job} at {selected_company}")
    st.caption("Simulated compensation progression from entry-level to senior leadership.")

    # Generate progression points across 0 to 18 years
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
        traj_records.append({"Experience": step, "Predicted_Salary": p_val, "P10": p10_step, "P90": p90_step})

    traj_df = pd.DataFrame(traj_records)

    # Line Chart with Confidence Envelope
    fig_traj = go.Figure()

    # Upper bound
    fig_traj.add_trace(go.Scatter(x=traj_df["Experience"], y=traj_df["P90"], mode="lines", line=dict(width=0), showlegend=False, name="P90"))
    # Lower bound with fill
    fig_traj.add_trace(go.Scatter(x=traj_df["Experience"], y=traj_df["P10"], mode="lines", line=dict(width=0), fill="tonexty", fillcolor="rgba(31, 119, 180, 0.15)", name="Likely Range (10th-90th Pct)"))
    # Main trendline
    fig_traj.add_trace(go.Scatter(x=traj_df["Experience"], y=traj_df["Predicted_Salary"], mode="lines+markers", line=dict(color="#1f77b4", width=3), name="Estimated Salary"))

    # Mark user's current selection
    fig_traj.add_trace(
        go.Scatter(
            x=[selected_exp],
            y=[predicted_salary],
            mode="markers+text",
            marker=dict(size=14, color="red", symbol="diamond"),
            text=[f"Current: {selected_exp}y (₹{predicted_salary}L)"],
            textposition="top center",
            name="Your Selected Point",
        )
    )

    fig_traj.update_layout(
        title=f"Compensation Growth Curve ({selected_company} · {selected_job})",
        xaxis_title="Years of Experience",
        yaxis_title="Salary (LPA)",
        height=450,
        template="plotly_white",
    )
    st.plotly_chart(fig_traj, use_container_width=True)

    # Milestone Stages
    st.markdown("#### 🎯 Career Stage Milestones")
    st_col1, st_col2, st_col3, st_col4 = st.columns(4)
    st_col1.metric("Fresh Graduate (0-1y)", f"₹ {traj_df.loc[traj_df['Experience'] == 1.0, 'Predicted_Salary'].values[0]} LPA")
    st_col2.metric("Mid-Level (3-5y)", f"₹ {traj_df.loc[traj_df['Experience'] == 5.0, 'Predicted_Salary'].values[0]} LPA")
    st_col3.metric("Senior (7-9y)", f"₹ {traj_df.loc[traj_df['Experience'] == 9.0, 'Predicted_Salary'].values[0]} LPA")
    st_col4.metric("Lead / Principal (12-15y)", f"₹ {traj_df.loc[traj_df['Experience'] == 15.0, 'Predicted_Salary'].values[0]} LPA")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6: METHODOLOGY, METRICS & ATTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.subheader("ℹ️ Data Provenance & Methodology")
    st.markdown(
        f"""
### 📊 Dataset Origin
- **Source:** Compensation and review data scraped from [AmbitionBox](https://www.ambitionbox.com/salaries) in mid-2026.
- **Coverage:** **{len(companies)} companies** and **{len(all_job_titles)} unique job titles**.
- **Role Taxonomy:** Parsed into **{len(role_families)} Canonical Role Families** and **5 Seniority Levels** using rule-based NLP.
- **Employee Reviews & RAG Index:** **33,200+ review vectors** embedded via `all-MiniLM-L6-v2` and indexed with FAISS for semantic review retrieval.

### 🤖 Machine Learning Architecture (Voting Ensemble)
- **Architecture:** `sklearn.pipeline.Pipeline` with `ColumnTransformer` + `VotingRegressor`:
  - **Estimator 1:** `RandomForestRegressor` (400 trees, max depth 22).
  - **Estimator 2:** `HistGradientBoostingRegressor` (200 iterations, 31 max leaves).
- **Features Used:** `Company`, `Job_Title`, `Industry`, `Role_Family`, `Seniority_Level`, `Rating`, and `Avg_Exp`.
- **Holdout Evaluation Metrics:**
  - **R² Score:** `{metadata.get('r2_score', 'N/A')}` *(Improved from 0.4511 → 0.5655)*
  - **Mean Absolute Error (MAE):** `{metadata.get('mae_lpa', 'N/A')} LPA` *(Improved from 4.27 → 3.85 LPA)*
  - **Root Mean Squared Error (RMSE):** `{metadata.get('rmse_lpa', 'N/A')} LPA` *(Improved from 6.50 → 5.78 LPA)*

### 💡 Prediction Confidence Bands
Rather than a naive single-point estimate, this tool computes the distribution across all 400 decision trees in the Random Forest ensemble component.
The **Likely Range** captures the **10th to 90th percentile** of tree disagreement, giving users a transparent view of model certainty.

### ⚠️ Limitations & Good Practice
- AmbitionBox records are self-reported by job seekers and current employees; they may not reflect recent counter-offers or stock grants.
- Excluded factors: exact tech stack, education pedigree (e.g. tier-1 college), city-level cost of living, stock options / RSUs, and individual negotiation skill.
- Use this platform as a strategic compass for salary negotiations and market benchmarking, not as a legal or contractual quote.
"""
    )
    st.divider()
    st.caption("Built with Streamlit & Plotly · Voting Ensemble generated via scikit-learn · Data from AmbitionBox")
