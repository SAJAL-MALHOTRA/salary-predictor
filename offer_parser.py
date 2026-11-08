"""
offer_parser.py -- Automated Indian Tech Offer Letter & Compensation Annexure Parser.

Ingests uploaded PDF offer letters (via pdfplumber) or pasted text annexures.
Extracts:
  - Employer Name & Candidate Job Title / Role
  - Quoted Annual CTC (normalized to LPA)
  - Fixed Basic Salary & Allowances
  - Variable / Performance Bonus (rupees and percentage)
  - Joining / Sign-on Bonus & Clawback Period
  - Statutory Notice Period (days)
  - Gratuity Inclusion Flag & Amount
"""

import io
import re
from typing import Dict, Any, Union


def parse_numeric_rupees(val_str: str) -> float:
    """Normalize raw rupee string (e.g. '12,50,000' or '12.5 LPA') to LPA float."""
    if not val_str:
        return 0.0
    clean = val_str.replace(",", "").strip().lower()
    clean = re.sub(r"[^\d.]", "", clean)
    if not clean:
        return 0.0
    num = float(clean)
    # If the number is large (e.g. 1,200,000 or 450,000), convert to LPA
    if num >= 100000:
        return round(num / 100000.0, 2)
    elif num >= 1000:
        return round(num / 100000.0, 2)
    return round(num, 2)


def extract_text_from_pdf(pdf_source: Union[bytes, io.BytesIO]) -> str:
    """Extract clean raw text from a PDF file using pdfplumber."""
    try:
        import pdfplumber
        if isinstance(pdf_source, bytes):
            pdf_source = io.BytesIO(pdf_source)
        full_text = []
        with pdfplumber.open(pdf_source) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text.append(text)
                # Also extract any tables on the page
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        row_clean = [str(c).strip() for c in row if c is not None]
                        if row_clean:
                            full_text.append(" | ".join(row_clean))
        return "\n".join(full_text)
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


def parse_offer_text(raw_text: str) -> Dict[str, Any]:
    """
    Parse offer letter or compensation annexure text with regex and heuristics.
    Returns normalized dictionary ready to feed into Offer Evaluator.
    """
    if not raw_text or not raw_text.strip():
        return {"error": "Empty text provided", "confidence": 0.0}

    text = raw_text

    # 1. Company Name Extraction
    detected_company = "Infosys"
    known_companies = [
        "Google", "Microsoft", "Amazon", "Uber", "Flipkart", "Swiggy", "Zomato",
        "Razorpay", "Paytm", "TCS", "Tata Consultancy Services", "Infosys", "Wipro",
        "Cognizant", "HCLTech", "HCL", "Tech Mahindra", "Accenture", "Deloitte",
        "Goldman Sachs", "J.P. Morgan", "JPMorgan", "Thoughtworks", "Publicis Sapient",
        "Nagarro", "EPAM", "LTIMindtree", "Capgemini", "Zepto", "Blinkit", "CRED",
        "PhonePe", "Groww", "Sprinklr", "Atlassian", "Adobe", "Intuit", "Salesforce"
    ]
    for comp in known_companies:
        if re.search(r"\b" + re.escape(comp) + r"\b", text, re.IGNORECASE):
            detected_company = comp
            break

    # 2. Role / Designation Extraction
    detected_role = "Senior Software Engineer"
    role_match = re.search(
        r"(?:Designation|Role|Position|Job Title)\s*[:\-]\s*([A-Za-z0-9\s/–-]+?)(?:\r?\n|,|\.|\()",
        text,
        re.IGNORECASE,
    )
    if role_match:
        role_candidate = role_match.group(1).strip()
        if len(role_candidate) > 2 and len(role_candidate) < 60:
            detected_role = role_candidate

    # 3. Quoted Annual CTC Extraction
    detected_ctc = 12.0
    ctc_patterns = [
        r"(?:Total\s+CTC|Cost\s+to\s+Company|Annual\s+CTC|Annual\s+Gross|Total\s+Gross\s+Package|Total\s+Annual\s+Remuneration)\s*[:\-|]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(?:LPA|Lakhs?|per\s+annum)?",
        r"(?:CTC|Total\s+Compensation)\s*[:\-|]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(?:LPA|Lakhs?|per\s+annum)",
        r"(?:INR|Rs\.?|₹)\s*([\d,]+(?:\.\d+)?)\s*(?:LPA|Lakhs?|per\s+annum)\s*(?:CTC|Cost\s+to\s+Company)",
    ]
    for pat in ctc_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = parse_numeric_rupees(m.group(1))
            if 1.0 <= val <= 250.0:
                detected_ctc = val
                break

    # 4. Basic Salary Extraction
    basic_patterns = [
        r"(?:Basic\s+Salary|Basic\s+Pay|Basic)\s*[:\-|]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)",
    ]
    detected_basic_lpa = None
    for pat in basic_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = parse_numeric_rupees(m.group(1))
            if 0.5 <= val <= 100.0:
                detected_basic_lpa = val
                break

    # 5. Variable / Performance Pay Extraction
    detected_var_pct = 15
    detected_var_lpa = 0.0
    var_patterns = [
        r"(?:Variable\s+Pay|Variable\s+Bonus|Performance\s+Pay|Performance\s+Bonus|Annual\s+Incentive)\s*[:\-|]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(?:%|LPA|Lakhs?)?",
        r"(\d{1,2})\s*%\s*(?:of\s+CTC\s+as\s+)?(?:variable|performance\s+bonus|incentive)",
    ]
    for pat in var_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw_str = m.group(1).replace(",", "").strip()
            num = float(raw_str)
            if "%" in m.group(0) or (num >= 5 and num <= 60 and "." not in raw_str):
                detected_var_pct = int(min(60, max(0, num)))
            else:
                lpa_val = parse_numeric_rupees(raw_str)
                if lpa_val > 0 and detected_ctc > 0:
                    detected_var_lpa = lpa_val
                    detected_var_pct = int(round((detected_var_lpa / detected_ctc) * 100))
            break

    # 6. Joining / Sign-on Bonus Extraction
    detected_jb_lpa = 0.0
    jb_patterns = [
        r"(?:Joining\s+Bonus|Sign-on\s+Bonus|Sign\s+on\s+Bonus|One-time\s+Bonus|Joining\s+Incentive)\s*[:\-|]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)",
    ]
    for pat in jb_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = parse_numeric_rupees(m.group(1))
            if 0.2 <= val <= 50.0:
                detected_jb_lpa = val
                break

    # 7. Clawback Window Extraction
    detected_clawback_months = 12 if detected_jb_lpa > 0 else 0
    clawback_match = re.search(
        r"(?:clawback|repay|refund|recover(?:ed)?)\s+(?:within|period)?\s*[:\-]?\s*(\d{1,2})\s*(?:months|year)",
        text,
        re.IGNORECASE,
    )
    if clawback_match:
        c_num = int(clawback_match.group(1))
        if "year" in clawback_match.group(0).lower():
            c_num *= 12
        detected_clawback_months = c_num

    # 8. Notice Period Extraction
    detected_np = 90
    np_match = re.search(
        r"(?:notice\s+period|notice\s+of)\s*[:\-]?\s*(\d{1,3})\s*(?:days|months)",
        text,
        re.IGNORECASE,
    )
    if np_match:
        n_num = int(np_match.group(1))
        if "month" in np_match.group(0).lower():
            n_num *= 30
        if 15 <= n_num <= 180:
            detected_np = n_num

    # 9. Gratuity Inclusion Flag
    detected_grat_included = True
    if re.search(r"gratuity\s+(?:is\s+)?(?:not\s+included|excluded|over\s+and\s+above)", text, re.IGNORECASE):
        detected_grat_included = False
    elif re.search(r"gratuity\s*(?:[:\-|]|\(?included|\(?as\s+per)", text, re.IGNORECASE):
        detected_grat_included = True

    # 10. Variable Payout Frequency
    detected_vfreq = "Annual Payout (High Forfeiture Risk)"
    if re.search(r"quarterly\s+(?:variable|bonus|disbursement|payout)", text, re.IGNORECASE):
        detected_vfreq = "Quarterly Payout"

    # Compute extraction confidence score
    confidence = 0.5
    if detected_ctc != 12.0:
        confidence += 0.2
    if detected_company != "Infosys":
        confidence += 0.15
    if role_match:
        confidence += 0.15

    return {
        "company": detected_company,
        "role": detected_role,
        "ctc_lpa": detected_ctc,
        "basic_lpa": detected_basic_lpa,
        "variable_pct": detected_var_pct,
        "joining_bonus_lpa": detected_jb_lpa,
        "clawback_months": detected_clawback_months,
        "notice_period_days": detected_np,
        "gratuity_included": detected_grat_included,
        "variable_freq": detected_vfreq,
        "confidence": min(1.0, confidence),
        "raw_text_preview": text[:500] + ("..." if len(text) > 500 else ""),
    }
