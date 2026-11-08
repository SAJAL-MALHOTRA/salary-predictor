"""
decision_matrix.py -- Multi-Offer Comparative Decision & Risk Scoring Engine.

Compares Offer A vs. Offer B vs. Current Baseline.
Computes:
  - Monthly In-Hand Net Bank Credit Delta
  - Risk-Adjusted Compensation Index (0-100)
  - Career Mobility & Notice Period Friction
  - Notice Buyout Breakeven Timeline
  - Executive Tradeoff Verdict
"""

from typing import Dict, Any


def evaluate_offer_profile(
    name: str,
    ctc_lpa: float,
    variable_pct: float,
    joining_bonus_lpa: float,
    notice_period_days: int,
    gratuity_included: bool,
    expected_tenure_years: float,
    take_home_monthly: float,
    guaranteed_year1_cash_lpa: float,
    tier_num: int,
) -> Dict[str, Any]:
    """Calculate normalized scores and risk weights for a single offer profile."""
    # 1. Guaranteed Cash Score (0 to 40 pts)
    # Higher guaranteed cash relative to CTC yields higher financial stability
    guar_ratio = guaranteed_year1_cash_lpa / max(1.0, ctc_lpa)
    guar_score = min(40.0, guar_ratio * 40.0)

    # 2. Monthly Take-home Score (0 to 35 pts)
    # Scaled logarithmically/linearly up to 2.5 Lakhs/month
    take_home_score = min(35.0, (take_home_monthly / 200000.0) * 35.0)

    # 3. Career Mobility & Notice Score (0 to 15 pts)
    # 30 days = 15 pts, 60 days = 10 pts, 90 days = 3 pts
    if notice_period_days <= 30:
        mobility_score = 15.0
    elif notice_period_days <= 60:
        mobility_score = 10.0
    else:
        mobility_score = 3.0

    # 4. Employer Tier & Stability Score (0 to 10 pts)
    tier_points = {1: 10.0, 2: 8.5, 3: 7.0, 4: 5.0}
    tier_score = tier_points.get(tier_num, 7.0)

    # Composite Index (0 to 100)
    composite_score = round(guar_score + take_home_score + mobility_score + tier_score, 1)

    return {
        "name": name,
        "ctc_lpa": float(ctc_lpa),
        "variable_pct": float(variable_pct),
        "joining_bonus_lpa": float(joining_bonus_lpa),
        "notice_period_days": int(notice_period_days),
        "take_home_monthly": int(take_home_monthly),
        "guaranteed_year1_cash_lpa": float(guaranteed_year1_cash_lpa),
        "guar_score": round(guar_score, 1),
        "mobility_score": round(mobility_score, 1),
        "tier_score": round(tier_score, 1),
        "composite_score": min(100.0, composite_score),
    }


def compare_two_offers(
    profile_a: Dict[str, Any],
    profile_b: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compare Offer A vs Offer B side-by-side with delta analysis and breakeven timelines.
    """
    # Net in-hand monthly difference
    diff_monthly = profile_b["take_home_monthly"] - profile_a["take_home_monthly"]
    diff_annual_net = diff_monthly * 12

    # Guaranteed cash delta
    diff_guaranteed_lpa = round(profile_b["guaranteed_year1_cash_lpa"] - profile_a["guaranteed_year1_cash_lpa"], 2)

    # Notice period difference
    notice_diff = profile_b["notice_period_days"] - profile_a["notice_period_days"]

    # Notice Buyout Breakeven
    # If Offer B has a buyout cost or notice friction, calculate how fast extra net income repays it
    est_buyout_cost_rupees = (profile_a["ctc_lpa"] * 100000.0 * 0.40 / 12.0) * (notice_diff / 30.0) if notice_diff > 0 else 0.0
    if diff_monthly > 0 and est_buyout_cost_rupees > 0:
        breakeven_months = round(est_buyout_cost_rupees / diff_monthly, 1)
        breakeven_text = f"Notice buyout recovers in {breakeven_months} months from Offer B's extra net salary."
    elif diff_monthly <= 0 and notice_diff > 0:
        breakeven_text = "Negative ROI: Offer B increases notice lock without delivering higher monthly in-hand cash."
    else:
        breakeven_text = "Zero notice friction: Immediate positive monthly cash flow."

    # Verdict synthesis
    if profile_b["composite_score"] > profile_a["composite_score"] + 5:
        verdict_title = f"{profile_b['name']} is the statistically superior offer"
        verdict_color = "#079669"
    elif profile_a["composite_score"] > profile_b["composite_score"] + 5:
        verdict_title = f"{profile_a['name']} provides superior risk-adjusted stability"
        verdict_color = "#4F46E5"
    else:
        verdict_title = "Offers are closely matched; choice depends on cash vs mobility preference"
        verdict_color = "#D97706"

    return {
        "profile_a": profile_a,
        "profile_b": profile_b,
        "diff_monthly": diff_monthly,
        "diff_annual_net": diff_annual_net,
        "diff_guaranteed_lpa": diff_guaranteed_lpa,
        "notice_diff": notice_diff,
        "breakeven_text": breakeven_text,
        "verdict_title": verdict_title,
        "verdict_color": verdict_color,
    }
