"""
company_tiers.py -- Employer Tier Classification & Negotiation Playbook Engine.

Categorizes Indian tech employers into 4 canonical compensation tiers:
  Tier 1: Global Tech & Elite GCCs (Google, Microsoft, Uber, Atlassian)
  Tier 2: Unicorns & High-Growth Product (Swiggy, Zomato, Razorpay, Flipkart)
  Tier 3: Specialized Digital Consultancies (Thoughtworks, Publicis Sapient, Nagarro)
  Tier 4: Enterprise IT Services (TCS, Infosys, Wipro, Cognizant, Accenture)

Provides tier-specific contract expectations and tactical negotiation guidance.
"""

import re

TIER_1_FIRMS = {
    "google", "microsoft", "amazon", "meta", "apple", "uber", "atlassian",
    "adobe", "intuit", "salesforce", "oracle", "cisco", "intel", "nvidia",
    "amd", "goldman sachs", "morgan stanley", "j.p. morgan", "jpmorgan",
    "d.e. shaw", "tower research", "rippling", "linkedin", "paypal",
    "stripe", "twilio", "walmart", "target", "booking.com", "expedia"
}

TIER_2_FIRMS = {
    "flipkart", "swiggy", "zomato", "razorpay", "cred", "phonepe",
    "paytm", "zerodha", "meesho", "dream11", "inmobi", "sprinklr",
    "groww", "urban company", "nykaa", "zepto", "blinkit", "slice",
    "jupiter", "browserstack", "postman", "freshworks", "ola", "curefit"
}

TIER_3_FIRMS = {
    "thoughtworks", "publicis sapient", "nagarro", "epam systems", "epam",
    "persistent systems", "persistent", "coforge", "hexaware", "virtusa",
    "birlasoft", "globallogic", "kpit", "cyient", "lti", "mphasis"
}

TIER_4_FIRMS = {
    "tcs", "tata consultancy services", "infosys", "wipro", "cognizant",
    "hcltech", "hcl", "tech mahindra", "ltimindtree", "capgemini",
    "accenture", "dxc technology", "dxc", "ntt data", "genpact", "tata elxsi"
}


def classify_employer_tier(company_name: str) -> dict:
    """
    Classify employer into Tier 1 to 4 with negotiation rules and contract baselines.
    """
    c = str(company_name).lower().strip()

    # Exact or keyword matching
    for firm in TIER_1_FIRMS:
        if firm in c:
            return {
                "tier_num": 1,
                "tier_name": "Tier 1: Global Tech & Elite GCC",
                "tier_badge": "Tier 1: Global Tech",
                "badge_color": "badge-indigo",
                "typical_notice_days": 30,
                "equity_structure": "Public RSUs (Liquid USD shares with quarterly vesting)",
                "variable_norm": "10–15% bonus target (historically pays ≥100%)",
                "negotiation_playbook": (
                    "Base pay in this tier is strictly bracketed by job level (e.g. L4/L5). "
                    "Do not waste leverage arguing base salary bands. Instead, push for higher "
                    "Year-1/Year-2 sign-on bonuses and increased upfront RSU grants, where hiring "
                    "managers possess wide discretionary authority."
                ),
            }

    for firm in TIER_2_FIRMS:
        if firm in c:
            return {
                "tier_num": 2,
                "tier_name": "Tier 2: Unicorn & High-Growth Product",
                "tier_badge": "Tier 2: Product Unicorn",
                "badge_color": "badge-emerald",
                "typical_notice_days": 60,
                "equity_structure": "ESOPs (1-year cliff, quarterly vesting; ask for last 409A / buyback history)",
                "variable_norm": "10–20% performance bonus (typically pays 80–90%)",
                "negotiation_playbook": (
                    "High-growth unicorns are sensitive to cash burn but generous with equity and signing bonuses. "
                    "If base salary hits internal ceilings, request guaranteed sign-on compensation or faster "
                    "ESOP vesting triggers. Always verify exercise window duration post-departure (aim for >2 years)."
                ),
            }

    for firm in TIER_3_FIRMS:
        if firm in c:
            return {
                "tier_num": 3,
                "tier_name": "Tier 3: Specialized Digital Consultancy",
                "tier_badge": "Tier 3: Product Consultancy",
                "badge_color": "badge-amber",
                "typical_notice_days": 60,
                "equity_structure": "Cash-only compensation (occasional phantom stock)",
                "variable_norm": "15–20% variable (disbursed quarterly or semi-annually based on billing)",
                "negotiation_playbook": (
                    "Consultancies link compensation directly to billable client rates. If your tech stack "
                    "is in high client demand (e.g. Cloud Native, Data Engineering, AI/ML), anchor your counter "
                    "around the 75th percentile and request quarterly variable payouts rather than annual."
                ),
            }

    for firm in TIER_4_FIRMS:
        if firm in c:
            return {
                "tier_num": 4,
                "tier_name": "Tier 4: Enterprise IT Services & SI",
                "tier_badge": "Tier 4: Enterprise Services",
                "badge_color": "badge-slate",
                "typical_notice_days": 90,
                "equity_structure": "Cash-only; no equity compensation",
                "variable_norm": "15–25% variable pay (often reduced by company-wide utilization and margin gates)",
                "negotiation_playbook": (
                    "Enterprise IT service recruiters face strict band ceilings governed by HR councils. "
                    "Countering >20% above band will trigger rejection. The winning tactic: accept the top-of-band "
                    "base, but negotiate to convert 5–10% of variable pay into fixed monthly allowance and demand "
                    "a joining bonus to offset notice period recovery."
                ),
            }

    # Default heuristic classification if company is unindexed
    return {
        "tier_num": 3,
        "tier_name": "Mid-Market / Independent Tech",
        "tier_badge": "Mid-Tier Tech",
        "badge_color": "badge-slate",
        "typical_notice_days": 60,
        "equity_structure": "Standard cash compensation with performance bonus",
        "variable_norm": "10–15% variable pay",
        "negotiation_playbook": (
            "Anchor your counter on verified role family benchmarks. Highlight specific stack expertise and "
            "request that variable pay terms specify individual performance criteria rather than company billing."
        ),
    }
