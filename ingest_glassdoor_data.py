"""
ingest_glassdoor_data.py -- Fetch, clean, and normalize the Kaggle Glassdoor India
Software Industry Salary Dataset (22,700+ records across 11,000+ companies).

Data source:
- Kaggle: ruchi798/software-industry-salary-dataset-2022
- Direct public research mirror (CC0 / Open Data)
- 100% legal, open academic research dataset.

Outputs saved to salary-predictor/:
- glassdoor_salaries_cleaned.csv: Cleaned & normalized Glassdoor India records
- glassdoor_benchmarks.json: Pre-aggregated benchmarks per company for UI display
"""

import json
import re
import urllib.request
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

DATASET_URL = "https://raw.githubusercontent.com/ntclai/Analysis-on-Software-Industry-in-India/main/Salary_Dataset_with_Extra_Features.csv"

# Alias mapping for tricky company names
COMPANY_ALIASES = {
    "TCS": ["tata consultancy services", "tcs"],
    "Infosys": ["infosys"],
    "Wipro": ["wipro"],
    "Cognizant": ["cognizant technology solutions", "cognizant"],
    "HCLTech": ["hcl technologies", "hcl"],
    "Tech Mahindra": ["tech mahindra"],
    "Accenture": ["accenture"],
    "Capgemini": ["capgemini"],
    "Deloitte": ["deloitte"],
    "IBM": ["ibm"],
    "Google": ["google"],
    "Microsoft": ["microsoft"],
    "Amazon": ["amazon"],
    "Flipkart": ["flipkart"],
    "Paytm": ["paytm", "one97"],
    "Samsung": ["samsung"],
    "Oracle": ["oracle"],
    "Cisco": ["cisco"],
    "Intel": ["intel"],
    "Qualcomm": ["qualcomm"],
    "Adobe": ["adobe"],
    "Uber": ["uber"],
    "Swiggy": ["swiggy"],
    "Zomato": ["zomato"],
    "Razorpay": ["razorpay"],
    "Mphasis": ["mphasis"],
    "Hexaware": ["hexaware"],
    "LTIMindtree": ["mindtree", "larsen & toubro infotech", "lti"],
    "Persistent Systems": ["persistent systems"],
    "Cyient": ["cyient"],
    "Birlasoft": ["birlasoft"],
}

# NLP categorization function
def categorize_job(title: str):
    t = str(title).lower()
    seniority = "Mid-Level"
    if re.search(r"\b(intern|trainee|fresher|graduate|entry|junior|jr|assistant|associate 1|l1)\b", t) and not re.search(r"\b(senior|sr|lead|vp|avp|director|manager|head)\b", t):
        seniority = "Entry / Junior"
    elif re.search(r"\b(vp|vice president|avp|director|head|general manager|cxo|cto|cfo|partner)\b", t):
        seniority = "Executive / Director"
    elif re.search(r"\b(senior|sr|lead|principal|architect|specialist|tech lead|team lead|staff|supervisor)\b", t):
        seniority = "Senior / Lead"
    elif re.search(r"\b(manager|program manager|project manager)\b", t):
        seniority = "Manager / Lead"

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
    else:
        role_family = "General Corporate & Services"

    return role_family, seniority


print("1. Downloading Kaggle Glassdoor India dataset...")
req = urllib.request.Request(DATASET_URL, headers={"User-Agent": "Mozilla/5.0"})
df_raw = pd.read_csv(urllib.request.urlopen(req))
print(f"   Downloaded {len(df_raw)} raw rows from Glassdoor India archive.")

# Clean salary bounds: ₹1 LPA to ₹100 LPA
df_clean = df_raw[(df_raw["Salary"] >= 100000) & (df_raw["Salary"] <= 10000000)].copy()
df_clean["Salary_LPA"] = round(df_clean["Salary"] / 100000.0, 2)
df_clean["comp_lower"] = df_clean["Company Name"].fillna("").astype(str).str.lower().str.strip()

# Apply NLP categorization
role_meta = df_clean["Job Title"].apply(lambda x: pd.Series(categorize_job(x), index=["Role_Family", "Seniority_Level"]))
df_clean["Role_Family"] = role_meta["Role_Family"]
df_clean["Seniority_Level"] = role_meta["Seniority_Level"]

print("2. Mapping against our canonical company names...")
with open(BASE_DIR / "company_insights.json", "r", encoding="utf-8") as f:
    company_insights = json.load(f)

our_companies = list(company_insights.keys())
glassdoor_benchmarks = {}
matched_records = []

for comp in our_companies:
    aliases = COMPANY_ALIASES.get(comp, [comp.lower()])
    matched_sub = pd.DataFrame()

    for alias in aliases:
        cand = df_clean[df_clean["comp_lower"].str.contains(alias, regex=False)]
        if len(cand) > 0:
            matched_sub = cand
            break

    if len(matched_sub) > 0:
        med_sal = round(float(matched_sub["Salary_LPA"].median()), 1)
        mean_sal = round(float(matched_sub["Salary_LPA"].mean()), 1)
        min_sal = round(float(matched_sub["Salary_LPA"].min()), 1)
        max_sal = round(float(matched_sub["Salary_LPA"].max()), 1)
        n_samples = len(matched_sub)
        top_locs = matched_sub["Location"].value_counts().head(3).index.tolist()
        top_roles = matched_sub["Job Title"].value_counts().head(3).index.tolist()

        glassdoor_benchmarks[comp] = {
            "source": "Glassdoor India (Kaggle Research Dataset)",
            "sample_count": n_samples,
            "median_salary_lpa": med_sal,
            "mean_salary_lpa": mean_sal,
            "min_salary_lpa": min_sal,
            "max_salary_lpa": max_sal,
            "top_locations": top_locs,
            "top_roles": top_roles,
        }

        for _, r in matched_sub.iterrows():
            matched_records.append({
                "Company": comp,
                "Original_Company_Name": r["Company Name"],
                "Job_Title": r["Job Title"],
                "Role_Family": r["Role_Family"],
                "Seniority_Level": r["Seniority_Level"],
                "Salary_LPA": r["Salary_LPA"],
                "Location": r["Location"],
                "Salaries_Reported": r.get("Salaries Reported", 1),
                "Rating": r.get("Rating", 3.8),
            })

print(f"3. Matched {len(glassdoor_benchmarks)} out of {len(our_companies)} companies ({len(matched_records)} individual records)!")

# Save pre-aggregated JSON benchmarks
json_path = BASE_DIR / "glassdoor_benchmarks.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(glassdoor_benchmarks, f, indent=2, ensure_ascii=False)
print(f"   Saved Glassdoor benchmarks JSON -> {json_path}")

# Save CSV of matched records
df_final = pd.DataFrame(matched_records)
csv_path = BASE_DIR / "glassdoor_salaries_cleaned.csv"
df_final.to_csv(csv_path, index=False)
print(f"   Saved cleaned Glassdoor CSV -> {csv_path} ({len(df_final)} rows)")

print("\nTop 10 Companies by Glassdoor Sample Size:")
for comp, data in sorted(glassdoor_benchmarks.items(), key=lambda x: x[1]["sample_count"], reverse=True)[:10]:
    print(f"  {comp:<20s} n={data['sample_count']:<4d} Median={data['median_salary_lpa']:5.1f} LPA  (Range: {data['min_salary_lpa']:.1f} - {data['max_salary_lpa']:.1f} LPA)")

print("\nGlassdoor India ingestion complete!")
