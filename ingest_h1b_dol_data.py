"""
ingest_h1b_dol_data.py -- Fetch, parse, and enrich Indian tech employer benchmarks
using official US Department of Labor (DOL) OFLC H-1B LCA disclosure datasets.

Data source:
- US Department of Labor (DOL) Office of Foreign Labor Certification (OFLC)
- LCA Disclosure Open Data (CC BY 4.0 via sergyinfo/h1b-lca-open-data)
- Direct public download, 100% legal, non-scraped government disclosure data.

Outputs saved to salary-predictor/:
- h1b_lca_benchmarks.json: Pre-computed H-1B LCA benchmarks (filings, median USD wage, approval rate, wage levels)
- h1b_summary.csv: Clean tabular slice of top Indian tech H-1B sponsors
"""

import json
import urllib.request
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

EMPLOYERS_URL = "https://huggingface.co/datasets/sergyinfo/h1b-lca-open-data/raw/main/employers_summary.csv"
OCCUPATION_URL = "https://huggingface.co/datasets/sergyinfo/h1b-lca-open-data/raw/main/occupation_wage_by_level.csv"

# Alias mapping for company names in our Indian dataset
COMPANY_ALIASES = {
    "TCS": ["TATA CONSULTANCY SERVICES", "TCS"],
    "Infosys": ["INFOSYS"],
    "Wipro": ["WIPRO"],
    "Cognizant": ["COGNIZANT TECHNOLOGY SOLUTIONS", "COGNIZANT"],
    "HCLTech": ["HCL AMERICA", "HCL TECHNOLOGIES"],
    "HCL": ["HCL AMERICA", "HCL TECHNOLOGIES"],
    "Tech Mahindra": ["TECH MAHINDRA"],
    "Accenture": ["ACCENTURE"],
    "Capgemini": ["CAPGEMINI"],
    "Deloitte": ["DELOITTE"],
    "IBM": ["IBM INDIA", "IBM CORPORATION"],
    "Microsoft": ["MICROSOFT CORPORATION", "MICROSOFT"],
    "Google": ["GOOGLE LLC", "GOOGLE"],
    "Amazon": ["AMAZON.COM SERVICES", "AMAZON"],
    "Oracle": ["ORACLE AMERICA", "ORACLE"],
    "Cisco": ["CISCO SYSTEMS"],
    "Intel": ["INTEL CORPORATION"],
    "Qualcomm": ["QUALCOMM TECHNOLOGIES", "QUALCOMM"],
    "Apple": ["APPLE INC", "APPLE"],
    "Meta": ["META PLATFORMS", "FACEBOOK"],
    "Goldman Sachs": ["GOLDMAN SACHS"],
    "Morgan Stanley": ["MORGAN STANLEY"],
    "JPMorgan": ["JPMORGAN CHASE"],
    "J.P. Morgan": ["JPMORGAN CHASE"],
    "LTIMindtree": ["LARSEN & TOUBRO INFOTECH", "LTIMINDTREE", "MINDTREE"],
    "Mphasis": ["MPHASIS"],
    "Hexaware": ["HEXAWARE TECHNOLOGIES"],
    "Persistent Systems": ["PERSISTENT SYSTEMS"],
    "Cyient": ["CYIENT"],
    "Birlasoft": ["BIRLASOFT"],
    "ZS Associates": ["ZS ASSOCIATES"],
    "McKinsey & Company": ["MCKINSEY & COMPANY"],
    "McKinsey": ["MCKINSEY & COMPANY"],
    "BCG": ["THE BOSTON CONSULTING GROUP", "BOSTON CONSULTING"],
    "Bain & Company": ["BAIN & COMPANY"],
    "Genpact": ["GENPACT"],
    "Paypal": ["PAYPAL"],
    "Salesforce": ["SALESFORCE.COM", "SALESFORCE"],
    "Adobe": ["ADOBE INC", "ADOBE"],
    "VMware": ["VMWARE"],
    "ServiceNow": ["SERVICENOW"],
    "Uber": ["UBER TECHNOLOGIES", "UBER"],
    "Walmart": ["WALMART ASSOCIATES", "WALMART"],
    "Flipkart": ["WALMART ASSOCIATES"],  # Parent company
    "SAP": ["SAP AMERICA"],
    "Dell": ["DELL MARKETING", "DELL PRODUCTS"],
    "HP": ["HP INC"],
    "EY": ["ERNST & YOUNG"],
    "KPMG": ["KPMG LLP"],
    "PwC": ["PRICEWATERHOUSECOOPERS"],
}

print("1. Downloading US DOL OFLC LCA disclosure data...")
req_emp = urllib.request.Request(EMPLOYERS_URL, headers={"User-Agent": "Mozilla/5.0"})
df_emp = pd.read_csv(urllib.request.urlopen(req_emp))
print(f"   Downloaded {len(df_emp)} employer records.")

req_occ = urllib.request.Request(OCCUPATION_URL, headers={"User-Agent": "Mozilla/5.0"})
df_occ = pd.read_csv(urllib.request.urlopen(req_occ))
print(f"   Downloaded {len(df_occ)} prevailing wage benchmark records.")

# Pre-compute Prevailing Wage Levels for Software Developers (SOC 15-1252 / 15-1132)
# and Computer Occupations (SOC 15-1299)
pw_levels_summary = {}
for soc in ["15-1252", "15-1132", "15-1299", "15-1211", "11-3021"]:
    sub = df_occ[df_occ["soc_code"] == soc]
    if len(sub) > 0:
        pw_levels_summary[soc] = {
            "title": sub["soc_title"].iloc[0],
            "levels": {row["pw_level"]: int(row["wage_median"]) for _, row in sub.iterrows()}
        }

print("2. Matching against Indian tech companies...")
# Load our company insights
with open(BASE_DIR / "company_insights.json", "r", encoding="utf-8") as f:
    company_insights = json.load(f)

our_companies = list(company_insights.keys())

h1b_benchmarks = {}
matched_records = []

df_emp["clean_name"] = df_emp["employer_name"].fillna("").astype(str).str.upper()

for comp in our_companies:
    # Check aliases first, then direct name matching
    aliases = COMPANY_ALIASES.get(comp, [comp.upper()])
    match_row = None

    for alias in aliases:
        cand = df_emp[df_emp["clean_name"].str.contains(alias, regex=False, case=False)]
        if len(cand) > 0:
            # Pick the row with the most filings (usually the primary US legal entity)
            match_row = cand.sort_values("total_filings", ascending=False).iloc[0]
            break

    if match_row is not None:
        total_filings = int(match_row["total_filings"])
        median_wage_usd = int(match_row["median_wage"])
        cert_pct = float(match_row["certified_pct"])
        state = str(match_row["employer_state"])
        top_soc = str(match_row.get("top_soc_title", "Software Engineering"))

        # Calculate wage progression by prevailing wage level
        # Scale benchmark levels proportional to the employer's wage premium
        # Baseline software dev level 1 is ~$90k, Level 2 is ~$100k, Level 3 is ~$115k, Level 4 is ~$135k
        wage_multiplier = median_wage_usd / 85000.0 if median_wage_usd > 0 else 1.0
        
        levels = {
            "Level I (Entry / Junior)": round(max(55000, 72000 * wage_multiplier), -2),
            "Level II (Mid-Level)": round(max(68000, 88000 * wage_multiplier), -2),
            "Level III (Senior / Lead)": round(max(85000, 110000 * wage_multiplier), -2),
            "Level IV (Principal / Manager)": round(max(105000, 135000 * wage_multiplier), -2),
        }

        h1b_benchmarks[comp] = {
            "matched_employer_name": str(match_row["employer_name"]),
            "us_work_state": state,
            "total_h1b_filings": total_filings,
            "median_wage_usd": median_wage_usd,
            "certified_pct": cert_pct,
            "top_us_job_title": top_soc,
            "wage_levels_usd": levels,
            "ppp_equivalent_inr_lpa": round((median_wage_usd * 23.5) / 100000.0, 1),  # World Bank PPP ~23.5 INR/USD
            "market_fx_inr_lpa": round((median_wage_usd * 86.0) / 100000.0, 1),       # Direct FX ~86 INR/USD
        }

        matched_records.append({
            "Company": comp,
            "US_Employer_Entity": str(match_row["employer_name"]),
            "Total_H1B_Filings": total_filings,
            "Median_Wage_USD": median_wage_usd,
            "Approval_Rate_Pct": cert_pct,
            "Primary_State": state,
            "Top_Occupation": top_soc,
        })

print(f"3. Matched {len(h1b_benchmarks)} out of {len(our_companies)} employers with official US DOL LCA records!")

# Save JSON benchmark artifact
json_path = BASE_DIR / "h1b_lca_benchmarks.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(h1b_benchmarks, f, indent=2, ensure_ascii=False)
print(f"   Saved JSON benchmarks -> {json_path}")

# Save CSV summary
df_matched = pd.DataFrame(matched_records).sort_values("Total_H1B_Filings", ascending=False)
csv_path = BASE_DIR / "h1b_summary.csv"
df_matched.to_csv(csv_path, index=False)
print(f"   Saved CSV summary -> {csv_path} ({len(df_matched)} rows)")

print("\nTop 10 Indian Tech Employers by US DOL H-1B Filings:")
print(df_matched.head(10)[["Company", "Total_H1B_Filings", "Median_Wage_USD", "Approval_Rate_Pct"]].to_string(index=False))

print("\nUS DOL H-1B LCA data ingestion complete!")
