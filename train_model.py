import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# Set random seed for reproducibility
np.random.seed(42)

# Define companies & tiers
company_tiers = {
    'Google': (22.0, 3.2),
    'Microsoft': (20.0, 3.0),
    'Amazon': (19.0, 2.8),
    'Uber': (21.0, 3.1),
    'Flipkart': (16.0, 2.5),
    'Swiggy': (14.0, 2.2),
    'Zomato': (13.5, 2.1),
    'Razorpay': (15.0, 2.3),
    'Paytm': (12.0, 2.0),
    'Goldman Sachs': (18.0, 2.7),
    'J.P. Morgan': (16.0, 2.4),
    'McKinsey & Company': (19.0, 2.9),
    'Deloitte': (10.0, 1.8),
    'Accenture': (8.0, 1.5),
    'Cognizant': (7.0, 1.4),
    'TCS': (5.5, 1.2),
    'Infosys': (5.8, 1.25),
    'Wipro': (5.6, 1.2),
    'HCLTech': (6.0, 1.3),
    'Tech Mahindra': (5.5, 1.25)
}

department_job_map = {
    'engineering-software-qa': [
        'Software Engineer', 'Senior Software Engineer', 'Lead Engineer',
        'Engineering Manager', 'QA Automation Engineer', 'DevOps Engineer',
        'Frontend Engineer', 'Backend Engineer', 'Full Stack Developer', 'System Architect'
    ],
    'data-science-analytics': [
        'Data Analyst', 'Data Scientist', 'Senior Data Scientist',
        'ML Engineer', 'Analytics Manager', 'BI Developer'
    ],
    'finance-accounting': [
        'Financial Analyst', 'Senior Accountant', 'Finance Manager', 'Investment Associate'
    ],
    'sales-business-development': [
        'Business Development Associate', 'Sales Executive', 'Account Executive', 'Sales Manager'
    ],
    'marketing-communication': [
        'Marketing Specialist', 'Content Marketer', 'SEO Analyst', 'Growth Marketing Manager'
    ],
    'human-resources': [
        'HR Executive', 'Technical Recruiter', 'HR Business Partner', 'HR Manager'
    ],
    'operations-supply-chain': [
        'Operations Manager', 'Supply Chain Analyst', 'Logistics Coordinator'
    ],
    'customer-success': [
        'Customer Success Specialist', 'Account Manager', 'Support Lead'
    ]
}

# Role level multiplier
role_multipliers = {
    'Software Engineer': 1.1,
    'Senior Software Engineer': 1.6,
    'Lead Engineer': 2.1,
    'Engineering Manager': 2.8,
    'QA Automation Engineer': 0.9,
    'DevOps Engineer': 1.3,
    'Frontend Engineer': 1.15,
    'Backend Engineer': 1.25,
    'Full Stack Developer': 1.2,
    'System Architect': 2.5,
    'Data Analyst': 1.0,
    'Data Scientist': 1.4,
    'Senior Data Scientist': 1.9,
    'ML Engineer': 1.5,
    'Analytics Manager': 2.2,
    'BI Developer': 1.1,
    'Financial Analyst': 1.1,
    'Senior Accountant': 1.2,
    'Finance Manager': 2.0,
    'Investment Associate': 1.8,
    'Business Development Associate': 0.85,
    'Sales Executive': 0.9,
    'Account Executive': 1.1,
    'Sales Manager': 1.8,
    'Marketing Specialist': 0.9,
    'Content Marketer': 0.8,
    'SEO Analyst': 0.85,
    'Growth Marketing Manager': 1.6,
    'HR Executive': 0.8,
    'Technical Recruiter': 1.0,
    'HR Business Partner': 1.4,
    'HR Manager': 1.7,
    'Operations Manager': 1.4,
    'Supply Chain Analyst': 1.0,
    'Logistics Coordinator': 0.8,
    'Customer Success Specialist': 0.85,
    'Account Manager': 1.2,
    'Support Lead': 1.0
}

# Generate 6500 rows
num_samples = 6500
records = []

companies = list(company_tiers.keys())
departments = list(department_job_map.keys())

for _ in range(num_samples):
    comp = np.random.choice(companies)
    dept = np.random.choice(departments)
    job = np.random.choice(department_job_map[dept])
    
    # Experience between 0 and 30
    exp = round(float(np.random.beta(2, 5) * 30), 1)
    
    base_sal, exp_coef = company_tiers[comp]
    role_mult = role_multipliers.get(job, 1.0)
    
    # Compute base salary formula with realistic non-linear scaling and noise
    exp_factor = (1 + exp ** 0.85 * 0.35 * exp_coef)
    noise = np.random.normal(1.0, 0.12)
    
    salary_lpa = max(2.5, round((base_sal * role_mult * exp_factor / 3.0) * noise, 2))
    
    records.append({
        'Company': comp,
        'Department': dept,
        'Job_Title': job,
        'Avg_Exp': exp,
        'Salary_LPA': salary_lpa
    })

df = pd.DataFrame(records)

# Save cleaned dataset for Streamlit UI dropdown population
df.to_csv('ambitionbox_salaries_cleaned.csv', index=False)
print(f"Dataset created with {len(df)} rows.")

# Feature Engineering pipeline matching app.py
X_raw = df[['Company', 'Department', 'Job_Title', 'Avg_Exp']]
y = df['Salary_LPA']

# One-hot encoding
X_encoded = pd.get_dummies(X_raw)
model_columns = X_encoded.columns.tolist()

# Train Random Forest Regressor
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.15, random_state=42)

rf_model = RandomForestRegressor(n_estimators=100, max_depth=16, min_samples_split=4, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

# Evaluate model
y_pred = rf_model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
print(f"Model Trained! Test R2 Score: {r2:.4f}, Test MAE: {mae:.2f} LPA")

# Save model artifacts
joblib.dump(rf_model, 'salary_rf_model.pkl')
joblib.dump(model_columns, 'model_columns.pkl')
print("Model artifacts ('salary_rf_model.pkl', 'model_columns.pkl') saved successfully.")
