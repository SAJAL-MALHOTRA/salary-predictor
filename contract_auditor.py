"""
contract_auditor.py -- Indian Tech Offer Contract Risk & Dark Pattern Auditor.

Audits statutory gratuity provisions (Payment of Gratuity Act 1972),
variable pay forfeiture timing, joining bonus clawback tax traps (Section 89(1)),
and computes True Guaranteed Year-1 Cash vs Paper CTC.
"""

def audit_offer_contract(
    ctc_lpa: float,
    variable_pct: float = 15.0,
    gratuity_included: bool = True,
    joining_bonus_lpa: float = 0.0,
    clawback_months: int = 12,
    notice_period_days: int = 90,
    variable_freq: str = "Annual",
    expected_tenure_years: float = 2.0,
) -> dict:
    """
    Perform a comprehensive contract risk audit on an Indian tech offer.
    Returns calculated financial leakage and legal dark pattern flags.
    """
    ctc_rupees = float(ctc_lpa) * 100000.0
    basic_rupees = ctc_rupees * 0.40  # 40% standard basic

    # 1. Statutory Gratuity Provision (Payment of Gratuity Act 1972, Section 4(1))
    # Statutory formula: (15 days / 26 working days) * monthly basic = ~4.8077% of annual basic
    annual_gratuity_rupees = basic_rupees * (15.0 / (26.0 * 12.0))

    if gratuity_included and expected_tenure_years < 5.0:
        phantom_gratuity_loss = annual_gratuity_rupees
        gratuity_flag = (
            f"⚠️ Phantom Gratuity Trap: ₹ {int(annual_gratuity_rupees):,}/year is included in your CTC sheet, "
            "but requires 5 continuous years under the Payment of Gratuity Act 1972. At an expected tenure of "
            f"{expected_tenure_years} years, you will receive ₹ 0 from this allocation."
        )
    elif gratuity_included:
        phantom_gratuity_loss = 0.0
        gratuity_flag = f"✅ Gratuity Eligible: Reaching 5 years qualifies you for accrued gratuity (₹ {int(annual_gratuity_rupees * expected_tenure_years):,} est. corpus)."
    else:
        phantom_gratuity_loss = 0.0
        gratuity_flag = "✅ Clean Structure: Gratuity is not deducted inside employee CTC."

    # 2. Variable Pay Risk & Resignation Timing
    variable_rupees = ctc_rupees * (float(variable_pct) / 100.0)
    fixed_ctc_rupees = ctc_rupees - variable_rupees

    if variable_freq.lower() == "annual" and variable_pct > 0:
        variable_timing_flag = (
            f"⚠️ Annual Variable Forfeiture Risk: Your {variable_pct}% variable pay (₹ {int(variable_rupees):,}) "
            "is disbursed annually. Resigning even 1 day prior to the appraisal payout letter forfeits 100% of accrued bonus."
        )
    elif variable_pct > 0:
        variable_timing_flag = (
            f"✅ Quarterly Variable: Your {variable_pct}% variable pay (₹ {int(variable_rupees):,}) "
            "is disbursed quarterly, significantly lowering departure forfeiture exposure."
        )
    else:
        variable_timing_flag = "✅ 100% Fixed Pay: Zero variable forfeiture exposure."

    # 3. Joining Bonus Clawback & Section 89(1) Tax Trap
    if joining_bonus_lpa > 0 and clawback_months >= 12:
        bonus_rupees = joining_bonus_lpa * 100000.0
        # Approx 31.2% TDS under peak New Tax Regime slab
        est_tds_paid = bonus_rupees * 0.312
        net_bonus_inhand = bonus_rupees - est_tds_paid
        clawback_flag = (
            f"⚠️ Section 89(1) Tax Clawback Trap: You received ₹ {int(bonus_rupees):,} gross (~₹ {int(net_bonus_inhand):,} in-hand after TDS). "
            f"If you exit within {clawback_months} months, the employer demands the full GROSS ₹ {int(bonus_rupees):,} back. "
            f"You will be out-of-pocket for ₹ {int(est_tds_paid):,} until filing Form 10E under Section 89(1) during your next ITR."
        )
    elif joining_bonus_lpa > 0:
        clawback_flag = f"✅ Short Clawback Window: Joining bonus lock is only {clawback_months} months."
    else:
        clawback_flag = "ℹ️ No joining bonus clawback clause on file."

    # 4. Notice Period & Buyout Reality
    if notice_period_days >= 90:
        notice_flag = (
            "⚠️ 90-Day Notice Lock: Discretionary buyout power rests entirely with the employer. "
            "IT services RMG desks frequently reject buyout requests, creating friction with future employers demanding 30-45 day joiners."
        )
    elif notice_period_days >= 60:
        notice_flag = "ℹ️ 60-Day Notice: Standard mid-tier notice period. Buyout usually approved with project sign-off."
    else:
        notice_flag = "✅ 30-Day Notice: Agile notice period. High market mobility."

    # 5. True Guaranteed Year-1 Cash vs Paper CTC
    guaranteed_year1_cash_rupees = fixed_ctc_rupees - phantom_gratuity_loss
    guaranteed_year1_cash_lpa = round(guaranteed_year1_cash_rupees / 100000.0, 2)
    paper_inflation_gap_rupees = ctc_rupees - guaranteed_year1_cash_rupees
    paper_inflation_gap_pct = round((paper_inflation_gap_rupees / ctc_rupees) * 100.0, 1)

    return {
        "quoted_ctc_lpa": float(ctc_lpa),
        "fixed_ctc_lpa": round(fixed_ctc_rupees / 100000.0, 2),
        "variable_lpa": round(variable_rupees / 100000.0, 2),
        "annual_gratuity_rupees": int(annual_gratuity_rupees),
        "phantom_gratuity_loss_rupees": int(phantom_gratuity_loss),
        "guaranteed_year1_cash_lpa": guaranteed_year1_cash_lpa,
        "paper_inflation_gap_rupees": int(paper_inflation_gap_rupees),
        "paper_inflation_gap_pct": paper_inflation_gap_pct,
        "gratuity_flag": gratuity_flag,
        "variable_timing_flag": variable_timing_flag,
        "clawback_flag": clawback_flag,
        "notice_flag": notice_flag,
    }
