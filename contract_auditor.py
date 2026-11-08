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

    # 6. Structured Risk Findings for FinTech Reporting
    structured_risks = []

    # Finding 1: Gratuity
    if gratuity_included and expected_tenure_years < 5.0:
        structured_risks.append({
            "category": "Statutory Deduction",
            "title": "Payment of Gratuity Act 1972 Forfeiture",
            "severity": "High Risk",
            "severity_level": "danger",
            "why_it_matters": (
                "Section 4(1) of the Act requires 5 years of continuous service to vest. "
                "Employers provision 4.81% of your basic pay inside your quoted CTC, but exiting "
                f"at {expected_tenure_years} years forfeits 100% of this accrued corpus."
            ),
            "financial_impact": f"₹ {int(annual_gratuity_rupees):,}/year uncollected (₹ 0 received at exit)",
            "verification_step": "Review the Annexure: confirm if gratuity is deducted inside Cost to Company or treated as an extra-CTC statutory benefit.",
        })
    elif gratuity_included:
        structured_risks.append({
            "category": "Statutory Deduction",
            "title": "Gratuity Eligible (5-Year Vesting Reached)",
            "severity": "Vested / Low Risk",
            "severity_level": "success",
            "why_it_matters": f"At an expected tenure of {expected_tenure_years} years, you cross the 5-year statutory threshold to claim accumulated gratuity.",
            "financial_impact": f"₹ {int(annual_gratuity_rupees * expected_tenure_years):,} estimated corpus receivable upon departure",
            "verification_step": "Verify gratuity calculation formula in employment agreement matches Section 4(2) of the Act (15/26 days per completed year).",
        })
    else:
        structured_risks.append({
            "category": "Statutory Deduction",
            "title": "Clean Gratuity Structure",
            "severity": "Clean",
            "severity_level": "success",
            "why_it_matters": "Gratuity is not deducted from employee monthly CTC.",
            "financial_impact": "₹ 0 deducted from offered cash",
            "verification_step": "Confirm no phantom gratuity line item exists in the detailed salary annexure.",
        })

    # Finding 2: Variable Pay Timing
    if variable_freq.lower() == "annual" and variable_pct > 0:
        structured_risks.append({
            "category": "Variable Compensation",
            "title": "Annual Bonus Resignation Lock",
            "severity": "High Risk",
            "severity_level": "danger",
            "why_it_matters": (
                f"Your {variable_pct}% variable pay is disbursed on an annual cycle. In most Indian tech firms, "
                "submitting a resignation letter prior to the formal bonus disbursement date results in 100% forfeiture of accrued bonus."
            ),
            "financial_impact": f"₹ {int(variable_rupees):,} at risk upon resignation timing",
            "verification_step": "Check the Employee Handbook clause: does bonus entitlement require 'active employee not serving notice on payout date'?",
        })
    elif variable_pct > 0:
        structured_risks.append({
            "category": "Variable Compensation",
            "title": "Quarterly Variable Distribution",
            "severity": "Moderate Caution",
            "severity_level": "warning",
            "why_it_matters": "Quarterly payouts significantly reduce lock-in risk, limiting forfeiture exposure to at most 1 quarter upon exit.",
            "financial_impact": f"₹ {int(variable_rupees / 4.0):,} maximum exposure per quarter",
            "verification_step": "Verify performance gate: is payout tied strictly to company revenue targets, individual KPIs, or manager discretion?",
        })
    else:
        structured_risks.append({
            "category": "Variable Compensation",
            "title": "100% Guaranteed Base Pay",
            "severity": "Guaranteed",
            "severity_level": "success",
            "why_it_matters": "Zero variable pay deduction. 100% of CTC is fixed cash flow.",
            "financial_impact": "₹ 0 at risk of appraisal forfeiture",
            "verification_step": "Confirm no hidden company billability or client-allocation contingency clauses in the appointment letter.",
        })

    # Finding 3: Joining Bonus Clawback
    if joining_bonus_lpa > 0 and clawback_months >= 12:
        bonus_rupees = joining_bonus_lpa * 100000.0
        est_tds_paid = bonus_rupees * 0.312
        net_bonus_inhand = bonus_rupees - est_tds_paid
        structured_risks.append({
            "category": "Sign-on Terms",
            "title": "Section 89(1) Tax Clawback Deficit",
            "severity": "High Risk",
            "severity_level": "danger",
            "why_it_matters": (
                f"You receive ₹ {int(bonus_rupees):,} gross (~₹ {int(net_bonus_inhand):,} in bank after TDS). "
                f"Exiting within {clawback_months} months requires repaying the full GROSS amount out-of-pocket, "
                "leaving you short until claiming relief under Section 89(1) Form 10E in the next financial year."
            ),
            "financial_impact": f"₹ {int(est_tds_paid):,} out-of-pocket tax cash flow deficit",
            "verification_step": "Request a pro-rata clawback clause (e.g. 1/12th amortized per completed month) rather than an all-or-nothing cliff.",
        })
    elif joining_bonus_lpa > 0:
        bonus_rupees = joining_bonus_lpa * 100000.0
        structured_risks.append({
            "category": "Sign-on Terms",
            "title": "Short Sign-on Clawback Window",
            "severity": "Moderate Caution",
            "severity_level": "warning",
            "why_it_matters": f"Clawback is limited to {clawback_months} months.",
            "financial_impact": f"₹ {int(bonus_rupees):,} gross repayment if departing before {clawback_months} months",
            "verification_step": "Verify repayment terms: check if net or gross recovery is mandated.",
        })

    # Finding 4: Notice Period
    if notice_period_days >= 90:
        structured_risks.append({
            "category": "Exit Mobility",
            "title": "90-Day Notice Lock & Buyout Discretion",
            "severity": "High Risk",
            "severity_level": "danger",
            "why_it_matters": (
                "Discretionary buyout power rests entirely with the employer. Indian IT Resource Management desks "
                "frequently decline buyout requests, causing prospective employers to rescind offers demanding 30-45 day joiners."
            ),
            "financial_impact": "Limits lateral mobility and makes counter-offers harder to leverage",
            "verification_step": "Confirm written buyout policy and ask if notice buyout is permitted during project release.",
        })
    elif notice_period_days >= 60:
        structured_risks.append({
            "category": "Exit Mobility",
            "title": "60-Day Notice Period",
            "severity": "Moderate Caution",
            "severity_level": "warning",
            "why_it_matters": "Standard mid-tier notice period. Buyouts are usually approved subject to team handover sign-off.",
            "financial_impact": "Manageable market transition window",
            "verification_step": "Confirm whether garden leave or buyout is standard upon voluntary exit.",
        })
    else:
        structured_risks.append({
            "category": "Exit Mobility",
            "title": "Agile Notice Period (30 Days)",
            "severity": "Agile Mobility",
            "severity_level": "success",
            "why_it_matters": "30-day notice allows rapid lateral hiring. High market mobility.",
            "financial_impact": "Negligible exit friction",
            "verification_step": "Confirm 30-day notice applies equally to employee and employer.",
        })

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
        "structured_risks": structured_risks,
    }
