"""
reddit_nlp_extractor.py -- NLP & Structuring Engine for Indian Tech Reddit Data.
Parses raw Reddit posts (r/developersIndia & r/cscareerquestionsIN), extracts:
- Real CTC figures, Base, Variable, and ESOPs (in LPA)
- Years of Experience (YoE)
- Canonical Company Aliases (118 employers)
- Indian Tech Dark Patterns & Red Flags (90-day notice, bench risks, PIP quotas, fake hikes)
- Developer Sentiment Polarity (-1.0 to +1.0)

Generates:
- reddit_benchmarks.json: Structured company intelligence for app.py
- reddit_threads_cleaned.csv: Flat dataset of parsed community submissions
"""

import json
from pathlib import Path
import re
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

# Aliases mapping informal developer slang to canonical company names
COMPANY_ALIASES = {
    "tcs": "TCS",
    "tata consultancy": "TCS",
    "tcs digital": "TCS",
    "tcs ninja": "TCS",
    "tcs prime": "TCS",
    "infy": "Infosys",
    "infosys": "Infosys",
    "mysore": "Infosys",
    "infosys sp": "Infosys",
    "wipro": "Wipro",
    "wipro turbo": "Wipro",
    "wipro elite": "Wipro",
    "cognizant": "Cognizant",
    "cts": "Cognizant",
    "genc": "Cognizant",
    "accenture": "Accenture",
    "atci": "Accenture",
    "hcl": "HCLTech",
    "hcltech": "HCLTech",
    "tech mahindra": "Tech Mahindra",
    "amazon": "Amazon",
    "amzn": "Amazon",
    "aws": "Amazon",
    "google": "Google",
    "goog": "Google",
    "microsoft": "Microsoft",
    "msft": "Microsoft",
    "idc": "Microsoft",
    "uber": "Uber",
    "flipkart": "Flipkart",
    "swiggy": "Swiggy",
    "zomato": "Zomato",
    "razorpay": "Razorpay",
    "paytm": "Paytm",
    "goldman": "Goldman Sachs",
    "goldman sachs": "Goldman Sachs",
    "jpmc": "JPMorgan Chase",
    "jpmorgan": "JPMorgan Chase",
    "deloitte": "Deloitte",
    "deloitte usi": "Deloitte",
    "oracle": "Oracle",
    "oci": "Oracle",
    "atlassian": "Atlassian",
    "capgemini": "Capgemini",
    "ltimindtree": "LTIMindtree",
    "mindtree": "LTIMindtree",
    "persistent": "Persistent Systems",
    "coforge": "Coforge",
    "mphasis": "Mphasis",
    "hexaware": "Hexaware",
    "cisco": "Cisco",
    "salesforce": "Salesforce",
    "adobe": "Adobe",
    "intel": "Intel",
    "qualcomm": "Qualcomm",
    "servicenow": "ServiceNow",
    "barclays": "Barclays",
    "wells fargo": "Wells Fargo",
    "morgan stanley": "Morgan Stanley",
}


def load_canonical_companies():
    """Load canonical company names from model_metadata.pkl if available."""
    metadata_path = BASE_DIR / "model_metadata.pkl"
    if metadata_path.exists():
        try:
            meta = joblib.load(metadata_path)
            return meta.get("companies", [])
        except Exception:
            pass
    return list(set(COMPANY_ALIASES.values()))


def match_companies(text, canonical_list):
    """Identify which companies are mentioned in a post."""
    text_lower = text.lower()
    matched = set()

    # 1. Match specific aliases
    for alias, canonical in COMPANY_ALIASES.items():
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, text_lower):
            matched.add(canonical)

    # 2. Match exact canonical names
    for comp in canonical_list:
        if comp.lower() in text_lower:
            matched.add(comp)

    return list(matched)


def extract_ctc_figures(text):
    """
    Extracts CTC, Base, and Variable figures in LPA from text.
    Handles '12 LPA', '34L', '28 Lakhs', '45L Base', etc.
    """
    ctc_candidates = []
    base_val = None
    var_val = None

    # Base salary patterns (e.g. 'Base: 28L', '28L Base', 'fixed: 30 LPA')
    base_match = re.search(r"(?:(?:base|fixed)(?:\s+salary)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:lpa|l|lakhs?)?|(\d+(?:\.\d+)?)\s*(?:lpa|l|lakhs?)?\s*(?:base|fixed))", text, re.IGNORECASE)
    if base_match:
        try:
            val_str = base_match.group(1) or base_match.group(2)
            val = float(val_str)
            if 2.0 <= val <= 150.0:
                base_val = val
        except (ValueError, TypeError):
            pass

    # Variable / Bonus patterns (e.g. 'Bonus: 5L', '5L Bonus', 'variable: 4 LPA')
    var_match = re.search(r"(?:(?:variable|bonus|sign[- ]?on)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:lpa|l|lakhs?)?|(\d+(?:\.\d+)?)\s*(?:lpa|l|lakhs?)?\s*(?:variable|bonus|sign[- ]?on))", text, re.IGNORECASE)
    if var_match:
        try:
            val_str = var_match.group(1) or var_match.group(2)
            val = float(val_str)
            if 0.5 <= val <= 40.0:
                var_val = val
        except (ValueError, TypeError):
            pass

    # General LPA / Lakhs pattern
    lpa_matches = re.finditer(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lac|l\b)", text, re.IGNORECASE)
    for m in lpa_matches:
        try:
            num = float(m.group(1))
            if 2.5 <= num <= 160.0:
                ctc_candidates.append(num)
        except ValueError:
            pass

    total_ctc = max(ctc_candidates) if ctc_candidates else (base_val or None)
    return total_ctc, base_val, var_val


def extract_yoe(text):
    """Extract years of experience from text."""
    if re.search(r"\bfresher\b|\b202[0-6]\s*batch\b|\bcollege\s*placement\b", text, re.IGNORECASE):
        return 0.0

    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:yoe|years?(?:\s*of)?\s*exp(?:erience)?)", text, re.IGNORECASE)
    if match:
        try:
            val = float(match.group(1))
            if 0.0 <= val <= 35.0:
                return val
        except ValueError:
            pass
    return None


def detect_red_flags(text):
    """
    Detects Indian Tech dark patterns:
    - 90-day notice period traps
    - Bench release / RMG termination threats
    - Silent PIP / stack-ranking quotas
    - Low appraisal percentages
    - Service bonds / clawback clauses
    """
    flags = {
        "notice_period_days": None,
        "notice_flag": False,
        "bench_risk": "Low",
        "pip_alert": False,
        "appraisal_leak": None,
        "bond_clause": False,
        "red_flag_score": 0,
    }
    text_lower = text.lower()

    # 1. Notice Period
    if re.search(r"\b90\s*(?:days?|day)\b|\b3\s*months?\b", text_lower):
        flags["notice_period_days"] = 90
        flags["notice_flag"] = True
        flags["red_flag_score"] += 25
    elif re.search(r"\b60\s*(?:days?|day)\b|\b2\s*months?\b", text_lower):
        flags["notice_period_days"] = 60
        flags["red_flag_score"] += 10
    elif re.search(r"\b30\s*(?:days?|day)\b|\b1\s*month\b", text_lower):
        flags["notice_period_days"] = 30

    # 2. Bench & Layoff Risk
    if re.search(r"\bbench\b.*(?:layoff|separation|rmg|fired|unbilled|ultimatum)", text_lower) or "survive bench" in text_lower:
        flags["bench_risk"] = "Severe"
        flags["red_flag_score"] += 30
    elif "bench" in text_lower:
        flags["bench_risk"] = "Moderate"
        flags["red_flag_score"] += 15

    # 3. PIP / Stack Ranking
    if re.search(r"\bpip\b|\bura\b|\bunregretted attrition\b|\bdev plan\b|\bforced attrition\b", text_lower):
        flags["pip_alert"] = True
        flags["red_flag_score"] += 25

    # 4. Service Bond / Clawback
    if re.search(r"\bbond\b|\bclawback\b|\bservice agreement\b|\bpenalty\b", text_lower):
        flags["bond_clause"] = True
        flags["red_flag_score"] += 20

    # 5. Appraisal Hike Reality
    hike_match = re.search(r"(\d+(?:\.\d+)?%?)\s*(?:to\s*(\d+(?:\.\d+)?%)?)?\s*(?:hike|appraisal)", text_lower)
    if hike_match:
        flags["appraisal_leak"] = hike_match.group(0).strip()
        if any(w in text_lower for w in ["0%", "1%", "2%", "3%", "delayed", "frozen"]):
            flags["red_flag_score"] += 15

    flags["red_flag_score"] = min(100, flags["red_flag_score"])
    return flags


def calculate_sentiment(text):
    """
    Computes text polarity and categorical sentiment:
    Positive, Neutral, Negative, or Toxic.
    """
    text_lower = text.lower()
    toxic_words = ["toxic", "trap", "exploit", "horrible", "scam", "threatened", "worst", "unethical", "nightmare"]
    negative_words = ["layoff", "lowball", "delayed", "cut", "bench", "pip", "micromanagement", "burnout", "frozen", "pain"]
    positive_words = ["great", "solid", "excellent", "best", "blessing", "transparent", "competitive", "perks", "chill", "wealth"]

    toxic_hits = sum(1 for w in toxic_words if w in text_lower)
    neg_hits = sum(1 for w in negative_words if w in text_lower)
    pos_hits = sum(1 for w in positive_words if w in text_lower)

    if toxic_hits >= 2 or (toxic_hits >= 1 and neg_hits >= 2):
        return -0.85, "Toxic"
    elif neg_hits > pos_hits:
        score = max(-0.75, -0.2 * (neg_hits - pos_hits))
        return score, "Negative"
    elif pos_hits > neg_hits:
        score = min(0.85, 0.25 * (pos_hits - neg_hits))
        return score, "Positive"
    else:
        return 0.05, "Neutral"


def evaluate_offer_verdict(ctc, yoe):
    """Render community verdict on compensation based on developer benchmarks."""
    if not ctc:
        return "Unspecified"
    if yoe is None:
        yoe = 3.0

    if yoe <= 1.0:
        if ctc < 4.0:
            return "Mass Recruiter Standard (Low)"
        elif ctc < 8.0:
            return "Solid Entry Tier (Digital/DSE)"
        elif ctc < 15.0:
            return "Tier-1 Fresher Package (SP/Fintech)"
        else:
            return "Top 1% Fresher (FAANG/Unicorn)"
    elif yoe <= 4.0:
        if ctc < 8.0:
            return "Service Firm Baseline (Lowball)"
        elif ctc < 16.0:
            return "Mid-Market Lateral"
        elif ctc < 30.0:
            return "Strong Product / FinTech Tier"
        else:
            return "Tier-1 Top Decile (FAANG/Uber)"
    else:
        if ctc < 18.0:
            return "Below Market Median"
        elif ctc < 35.0:
            return "Solid Lead/Architect Tier"
        else:
            return "Executive / Elite Comp"


def process_reddit_data(raw_json_path="reddit_raw_posts.json"):
    """Main processing pipeline: parses raw posts into structured benchmarks."""
    in_file = BASE_DIR / raw_json_path
    if not in_file.exists():
        print(f"[!] Input file {raw_json_path} not found. Running harvester first...")
        from reddit_harvester import run_harvester
        run_harvester(raw_json_path)

    with open(in_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    canonical_companies = load_canonical_companies()
    parsed_records = []
    company_groups = {}

    for post in posts:
        full_text = f"{post['title']}\n{post['body']}"
        for comment in post.get("top_comments", []):
            full_text += f"\n{comment.get('body', '')}"

        matched_comps = match_companies(full_text, canonical_companies)
        if not matched_comps:
            matched_comps = ["General Tech Ecosystem"]

        ctc, base, var = extract_ctc_figures(full_text)
        yoe = extract_yoe(full_text)
        flags = detect_red_flags(full_text)
        polarity, sentiment_label = calculate_sentiment(full_text)
        verdict = evaluate_offer_verdict(ctc, yoe)

        record = {
            "post_id": post["post_id"],
            "title": post["title"],
            "subreddit": post["subreddit"],
            "author": post["author"],
            "score": post["score"],
            "num_comments": post["num_comments"],
            "permalink": post["permalink"],
            "companies": matched_comps,
            "ctc_lpa": ctc,
            "base_lpa": base,
            "variable_lpa": var,
            "yoe": yoe,
            "notice_period_days": flags["notice_period_days"],
            "bench_risk": flags["bench_risk"],
            "pip_alert": flags["pip_alert"],
            "bond_clause": flags["bond_clause"],
            "appraisal_leak": flags["appraisal_leak"],
            "red_flag_score": flags["red_flag_score"],
            "sentiment_polarity": polarity,
            "sentiment_label": sentiment_label,
            "offer_verdict": verdict,
            "body_excerpt": post["body"][:250] + "...",
        }
        parsed_records.append(record)

        # Aggregate by company
        for comp in matched_comps:
            if comp not in company_groups:
                company_groups[comp] = []
            company_groups[comp].append(record)

    # Build company scorecards
    benchmarks = {}
    for comp, recs in company_groups.items():
        if comp == "General Tech Ecosystem":
            continue

        sentiments = [r["sentiment_label"] for r in recs]
        polarities = [r["sentiment_polarity"] for r in recs]
        avg_polarity = round(sum(polarities) / len(polarities), 2)

        # Count sentiment distribution
        pos_cnt = sentiments.count("Positive")
        neu_cnt = sentiments.count("Neutral")
        neg_cnt = sentiments.count("Negative")
        tox_cnt = sentiments.count("Toxic")
        total_s = len(sentiments)

        # Red flags aggregation
        notice_periods = [r["notice_period_days"] for r in recs if r["notice_period_days"]]
        predominant_notice = max(set(notice_periods), key=notice_periods.count) if notice_periods else 60
        bench_risks = [r["bench_risk"] for r in recs if r["bench_risk"] != "Low"]
        has_pip = any(r["pip_alert"] for r in recs)
        has_bond = any(r["bond_clause"] for r in recs)
        appraisal_notes = [r["appraisal_leak"] for r in recs if r["appraisal_leak"]]

        # Leaked CTCs
        leaked_ctcs = []
        for r in recs:
            if r["ctc_lpa"]:
                leaked_ctcs.append(
                    {
                        "ctc_lpa": r["ctc_lpa"],
                        "base_lpa": r["base_lpa"],
                        "yoe": r["yoe"],
                        "verdict": r["offer_verdict"],
                        "source_title": r["title"][:70],
                        "permalink": r["permalink"],
                    }
                )

        benchmarks[comp] = {
            "thread_count": len(recs),
            "avg_sentiment_polarity": avg_polarity,
            "sentiment_breakdown": {
                "positive_pct": round((pos_cnt / total_s) * 100, 1),
                "neutral_pct": round((neu_cnt / total_s) * 100, 1),
                "negative_pct": round((neg_cnt / total_s) * 100, 1),
                "toxic_pct": round((tox_cnt / total_s) * 100, 1),
            },
            "red_flags": {
                "notice_period_days": predominant_notice,
                "notice_risk_label": "High Risk (Restricted Mobility)" if predominant_notice == 90 else "Standard",
                "bench_risk_level": "Severe" if "Severe" in bench_risks else ("Moderate" if bench_risks else "Low"),
                "pip_quota_alert": has_pip,
                "service_bond_detected": has_bond,
                "reported_appraisals": appraisal_notes[0] if appraisal_notes else "Not reported",
            },
            "leaked_offers": sorted(leaked_ctcs, key=lambda x: x["ctc_lpa"], reverse=True),
            "top_threads": [
                {
                    "title": r["title"],
                    "score": r["score"],
                    "num_comments": r["num_comments"],
                    "permalink": r["permalink"],
                    "sentiment": r["sentiment_label"],
                    "excerpt": r["body_excerpt"],
                }
                for r in sorted(recs, key=lambda x: x["score"], reverse=True)[:3]
            ],
        }

    # Save artifacts
    bench_out = BASE_DIR / "reddit_benchmarks.json"
    with open(bench_out, "w", encoding="utf-8") as f:
        json.dump(benchmarks, f, indent=2, ensure_ascii=False)

    df_cleaned = pd.DataFrame(parsed_records)
    csv_out = BASE_DIR / "reddit_threads_cleaned.csv"
    df_cleaned.to_csv(csv_out, index=False, encoding="utf-8")

    print("=" * 70)
    print("  REDDIT DEVELOPER NLP EXTRACTION & STRUCTURING COMPLETE")
    print("=" * 70)
    print(f"[+] Total Threads Processed: {len(parsed_records)}")
    print(f"[+] Companies Benchmarked: {len(benchmarks)}")
    print(f"[+] Generated: {bench_out.name} ({bench_out.stat().st_size / 1024:.1f} KB)")
    print(f"[+] Generated: {csv_out.name} ({csv_out.stat().st_size / 1024:.1f} KB)")
    print("=" * 70)
    return benchmarks, df_cleaned


if __name__ == "__main__":
    process_reddit_data()
