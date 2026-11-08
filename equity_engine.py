"""
equity_engine.py -- Total Rewards, Equity Vesting & Tax Valuation Engine.

Models compensation for Indian tech professionals across:
  1. Global Tech RSUs (Public liquid equity, USD/INR conversion, Section 17(2) perquisite tax)
  2. Indian Startup ESOPs (Private options, 4-year vesting, 1-year cliff, liquidity haircuts)
  3. The 90-Day Post-Termination Exercise Window Trap
  4. True Year-1 Total Rewards (Guaranteed Cash vs Liquid Equity vs Illiquid Paper Equity)
"""

from typing import Dict, Any


def evaluate_equity_component(
    equity_type: str = "RSU",  # "RSU" or "ESOP"
    grant_value_lpa: float = 12.0,  # Total 4-year grant value in ₹ LPA
    vesting_schedule: str = "Standard 25/25/25/25",  # "Standard 25/25/25/25", "Amazon 5/15/40/40", "Frontloaded 33/33/22/12"
    company_stage: str = "Public Tech / GCC",  # "Public Tech / GCC", "Late-Stage Unicorn (Frequent Buybacks)", "Early-Stage Startup"
    exercise_window_days: int = 90,  # Post-departure exercise window
    annual_base_ctc_lpa: float = 20.0,
) -> Dict[str, Any]:
    """
    Calculate Year 1 to Year 4 equity realization, liquidity haircuts, and tax liabilities.
    """
    grant_total = float(grant_value_lpa)

    # Vesting schedule percentage splits across [Year 1, Year 2, Year 3, Year 4]
    if "Amazon" in vesting_schedule:
        vest_splits = [0.05, 0.15, 0.40, 0.40]
        vest_label = "Amazon Back-Loaded (5% Y1, 15% Y2, 40% Y3, 40% Y4)"
    elif "Frontloaded" in vesting_schedule:
        vest_splits = [0.33, 0.33, 0.22, 0.12]
        vest_label = "Front-Loaded (33% Y1, 33% Y2, 22% Y3, 12% Y4)"
    else:
        vest_splits = [0.25, 0.25, 0.25, 0.25]
        vest_label = "Standard Equal Vesting (25% per year with 1-Year Cliff)"

    y1_vest_lpa = round(grant_total * vest_splits[0], 2)
    y2_vest_lpa = round(grant_total * vest_splits[1], 2)
    y3_vest_lpa = round(grant_total * vest_splits[2], 2)
    y4_vest_lpa = round(grant_total * vest_splits[3], 2)

    # Liquidity & Realization Haircut
    # Public RSUs: 100% liquid (0% discount)
    # Late-Stage Unicorns with buybacks: ~65% probability-adjusted value (35% discount)
    # Early-Stage Startups: ~30% probability-adjusted value (70% illiquidity haircut)
    if "Public" in company_stage or equity_type == "RSU":
        liquidity_factor = 1.00
        liquidity_desc = "Liquid Market Value: Listed public shares with quarterly brokerage liquidity."
    elif "Late-Stage" in company_stage:
        liquidity_factor = 0.65
        liquidity_desc = "Partial Liquidity: Unlisted shares dependent on corporate secondary buyback rounds."
    else:
        liquidity_factor = 0.30
        liquidity_desc = "Illiquid Paper Equity: Substantial discount until IPO or Series C+ liquidity event."

    y1_realizable_lpa = round(y1_vest_lpa * liquidity_factor, 2)

    # Perquisite Tax Liability under Section 17(2) of Indian Income Tax Act
    # Estimated 31.2% - 35.88% peak slab deduction upon vesting day
    est_perquisite_tax_rate = 0.312
    y1_perquisite_tax_lpa = round(y1_vest_lpa * est_perquisite_tax_rate, 2)
    y1_net_equity_lpa = round(y1_realizable_lpa - (y1_perquisite_tax_lpa if liquidity_factor == 1.0 else 0.0), 2)

    # Exercise Window Trap Audit
    exercise_trap_flags = []
    if equity_type == "ESOP" and exercise_window_days <= 90:
        exercise_trap_flags.append(
            f"⚠️ 90-Day Golden Handcuffs Trap: If you resign, you must exercise all vested options within {exercise_window_days} days. "
            "Because the startup is unlisted, you cannot sell shares to cover exercise cost or perquisite tax. "
            "You will be forced to pay hundreds of thousands of rupees out-of-pocket in cash or surrender 100% of your earned equity."
        )
    elif equity_type == "ESOP":
        exercise_trap_flags.append(
            f"✅ Progressive Exercise Policy: {exercise_window_days}-day window gives you reasonable time to plan option execution post-departure."
        )
    else:
        exercise_trap_flags.append(
            "✅ Public RSU Grant: Shares deposit directly into your broker (e.g. Morgan Stanley / E*TRADE). Zero exercise window pressure."
        )

    # Total Rewards Composition (Year 1)
    total_y1_quoted_rewards_lpa = round(annual_base_ctc_lpa + y1_vest_lpa, 2)
    total_y1_realizable_rewards_lpa = round(annual_base_ctc_lpa + y1_realizable_lpa, 2)

    return {
        "equity_type": equity_type,
        "grant_value_lpa": grant_total,
        "vesting_schedule_label": vest_label,
        "vest_splits": vest_splits,
        "y1_vest_lpa": y1_vest_lpa,
        "y2_vest_lpa": y2_vest_lpa,
        "y3_vest_lpa": y3_vest_lpa,
        "y4_vest_lpa": y4_vest_lpa,
        "liquidity_factor": liquidity_factor,
        "liquidity_desc": liquidity_desc,
        "y1_realizable_lpa": y1_realizable_lpa,
        "y1_perquisite_tax_lpa": y1_perquisite_tax_lpa,
        "y1_net_equity_lpa": y1_net_equity_lpa,
        "exercise_window_days": exercise_window_days,
        "exercise_trap_flags": exercise_trap_flags,
        "total_y1_quoted_rewards_lpa": total_y1_quoted_rewards_lpa,
        "total_y1_realizable_rewards_lpa": total_y1_realizable_rewards_lpa,
    }
