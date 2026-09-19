import streamlit as st
import joblib
import pandas as pd

# --- 1. CONFIGURATION & MODEL LOADING ---
st.set_page_config(page_title="AmbitionBox Salary Predictor", page_icon="💼", layout="centered")

@st.cache_resource
def load_assets():
    # Load model artifacts
    model = joblib.load('salary_rf_model.pkl')
    columns = joblib.load('model_columns.pkl')
    # Load cleaned dataset to populate our dropdown menus dynamically
    df = pd.read_csv('ambitionbox_salaries_cleaned.csv')
    return model, columns, df

model, columns, df = load_assets()

# --- 2. HEADER INTERFACE ---
st.title("💼 India Salary Predictor")
st.subheader("Powered by 6000+ real AmbitionBox data points")
st.divider()

# --- 3. INPUT FORM ---
col1, col2 = st.columns(2)

with col1:
    # Dropdown menu sorted alphabetically to easily find companies
    sorted_companies = sorted(df['Company'].unique())
    company = st.selectbox("Company Name", sorted_companies)
    
    # Filter job titles based on selected company so the UI is intuitive
    available_jobs = sorted(df[df['Company'] == company]['Job_Title'].unique())
    job_title = st.selectbox("Job Title", available_jobs)

with col2:
    department = st.selectbox("Department", [
        'engineering-software-qa',
        'finance-accounting',
        'sales-business-development',
        'marketing-communication',
        'human-resources',
        'operations-supply-chain',
        'customer-success',
        'data-science-analytics'
    ])
    avg_exp = st.slider("Years of Experience", 0.0, 30.0, 3.0, step=0.5)

st.divider()

# --- 4. PREDICTION PIPELINE ---
if st.button("Predict Salary 🚀", use_container_width=True):
    # Wrap active user selections into a dataframe structure
    input_data = pd.DataFrame([{
        'Company': company,
        'Department': department,
        'Job_Title': job_title,
        'Avg_Exp': float(avg_exp)
    }])
    
    # Process inputs through the exact same feature engineering pipeline
    encoded = pd.get_dummies(input_data)
    aligned = encoded.reindex(columns=columns, fill_value=0)
    prediction = model.predict(aligned)[0]

    # Present calculated output vividly
    st.success(f"### Predicted Salary: ₹ {prediction:.2f} LPA")
    st.caption(f"**Selection:** {company} | {job_title} | {avg_exp} years experience")

st.divider()
st.caption("Built by Sajal · Data from AmbitionBox · Model: Random Forest")
