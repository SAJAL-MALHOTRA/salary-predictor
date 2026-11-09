import type { ContractAuditResult, StructuredRisk } from '../types';

export function auditOfferContract(
  ctcLpa: number,
  variablePct: number = 15,
  gratuityIncluded: boolean = true,
  joiningBonusLpa: number = 0,
  clawbackMonths: number = 12,
  noticePeriodDays: number = 90,
  variableFreq: 'Annual' | 'Quarterly' = 'Annual',
  expectedTenureYears: number = 2.0
): ContractAuditResult {
  const ctcRupees = ctcLpa * 100000;
  const basicRupees = ctcRupees * 0.40;

  // Statutory Gratuity Provision (Payment of Gratuity Act 1972)
  // (15 days / 26 working days) * monthly basic = (15 / (26 * 12)) * annual basic = 4.8077% of basic
  const annualGratuityRupees = Math.round(basicRupees * (15.0 / (26.0 * 12.0)));
  const phantomGratuityLoss = gratuityIncluded && expectedTenureYears < 5.0 ? annualGratuityRupees : 0;

  // Variable Pay
  const variableRupees = Math.round(ctcRupees * (variablePct / 100.0));
  const fixedCtcRupees = ctcRupees - variableRupees;

  // Guaranteed Year-1 Cash
  const guaranteedYear1CashRupees = fixedCtcRupees - phantomGratuityLoss;
  const guaranteedYear1CashLpa = Math.round((guaranteedYear1CashRupees / 100000) * 100) / 100;

  // Paper CTC Inflation Gap
  const paperInflationGapRupees = ctcRupees - guaranteedYear1CashRupees;
  const paperInflationGapPct = Math.round((paperInflationGapRupees / ctcRupees) * 1000) / 10;

  const risks: StructuredRisk[] = [];

  // Finding 1: Gratuity Lock
  if (gratuityIncluded && expectedTenureYears < 5.0) {
    risks.push({
      id: 'gratuity-lock',
      category: 'Statutory Deduction Trap',
      title: 'Payment of Gratuity Act 1972 Forfeiture',
      clauseRef: 'Annexure A — Statutory Benefits Clause 4.1',
      clauseExcerpt: 'Gratuity will be payable strictly in accordance with the Payment of Gratuity Act, 1972.',
      severity: 'HIGH',
      whyItMatters: `Section 4(1) of the Act requires 5 continuous years of service. Indian tech median tenure is 2.2 years. At ${expectedTenureYears} years expected tenure, you forfeit 100% of this accrued CTC allocation.`,
      financialImpact: `₹ ${annualGratuityRupees.toLocaleString('en-IN')}/year deducted from cash (₹ 0 received at exit)`,
      verificationAction: 'Check whether gratuity is deducted inside your Cost to Company or paid as an extra-CTC employer benefit.',
      counterAmendment: 'Amend Annexure: "Gratuity to be treated as an extra-CTC statutory benefit, restoring ₹ ' + annualGratuityRupees.toLocaleString('en-IN') + ' into monthly Special Allowance."',
    });
  } else if (gratuityIncluded) {
    risks.push({
      id: 'gratuity-vested',
      category: 'Statutory Deduction',
      title: 'Gratuity Vested (5-Year Threshold Met)',
      clauseRef: 'Annexure A — Clause 4.1',
      clauseExcerpt: 'Gratuity calculated as per 15 days basic salary per completed year of service.',
      severity: 'CLEAN',
      whyItMatters: `At ${expectedTenureYears} years tenure, you qualify for statutory gratuity payout upon departure.`,
      financialImpact: `₹ ${(annualGratuityRupees * expectedTenureYears).toLocaleString('en-IN')} estimated accrued gratuity corpus receivable at exit`,
      verificationAction: 'Verify calculation matches Section 4(2) formula: (15 / 26) * last drawn basic * tenure.',
      counterAmendment: 'No amendment necessary.',
    });
  }

  // Finding 2: Variable Pay Lock
  if (variableFreq === 'Annual' && variablePct > 0) {
    risks.push({
      id: 'variable-annual-lock',
      category: 'Variable Compensation Risk',
      title: 'Annual Bonus Resignation Forfeiture Clause',
      clauseRef: 'Clause 5.2 — Annual Performance Pay Schedule',
      clauseExcerpt: 'Employee must be actively employed and not serving notice period on the date of annual bonus disbursement.',
      severity: 'HIGH',
      whyItMatters: `Your ${variablePct}% variable pay (₹ ${variableRupees.toLocaleString('en-IN')}) is locked into an annual cycle. Resigning even 1 day before the formal payout letter forfeits 100% of accrued performance pay.`,
      financialImpact: `₹ ${variableRupees.toLocaleString('en-IN')} unvested cash at risk upon resignation timing`,
      verificationAction: 'Inspect employee handbook: confirm if departure during notice period forfeits accrued pro-rata bonus.',
      counterAmendment: 'Amend Clause 5.2: "Variable incentive to be calculated and disbursed on a pro-rata quarterly basis regardless of notice status."',
    });
  } else if (variablePct > 0) {
    risks.push({
      id: 'variable-quarterly',
      category: 'Variable Compensation',
      title: 'Quarterly Variable Distribution',
      clauseRef: 'Clause 5.2 — Quarterly Incentive Program',
      clauseExcerpt: 'Variable bonus evaluated and paid on quarterly milestone achievement.',
      severity: 'MEDIUM',
      whyItMatters: 'Quarterly payout caps exit forfeiture exposure to at most 1 quarter rather than a full year.',
      financialImpact: `Maximum ₹ ${Math.round(variableRupees / 4).toLocaleString('en-IN')} exposure per quarter`,
      verificationAction: 'Confirm performance gate: is payout tied strictly to individual deliverables or company EBITDA/billability?',
      counterAmendment: 'Clarify objective individual KPI thresholds in writing.',
    });
  }

  // Finding 3: Joining Bonus Clawback
  if (joiningBonusLpa > 0 && clawbackMonths >= 12) {
    const jbRupees = joiningBonusLpa * 100000;
    const estTdsPaid = Math.round(jbRupees * 0.312);
    const netInHandBonus = jbRupees - estTdsPaid;

    risks.push({
      id: 'clawback-tax-trap',
      category: 'Sign-on Terms & Tax Risk',
      title: 'Section 89(1) Tax Clawback Deficit',
      clauseRef: 'Clause 6.3 — Joining Bonus Recovery',
      clauseExcerpt: `In the event of resignation within ${clawbackMonths} months, the employee shall repay the full gross joining bonus to the company.`,
      severity: 'HIGH',
      whyItMatters: `You receive ₹ ${jbRupees.toLocaleString('en-IN')} gross (~₹ ${netInHandBonus.toLocaleString('en-IN')} in bank after 31.2% TDS). Exiting early requires repaying the full GROSS ₹ ${jbRupees.toLocaleString('en-IN')} back out-of-pocket, creating an immediate ₹ ${estTdsPaid.toLocaleString('en-IN')} cash deficit until filing Form 10E during next year's ITR.`,
      financialImpact: `₹ ${estTdsPaid.toLocaleString('en-IN')} out-of-pocket tax deficit required to exit`,
      verificationAction: 'Request a pro-rata monthly amortization clause (1/12th forgiven per completed month) rather than an all-or-nothing cliff.',
      counterAmendment: 'Amend Clause 6.3: "Joining bonus recovery to be amortized on a pro-rata basis of 1/' + clawbackMonths + ' per completed month of active service."',
    });
  }

  // Finding 4: Notice Period Lock
  if (noticePeriodDays >= 90) {
    risks.push({
      id: 'notice-period-90',
      category: 'Exit Mobility & Market Friction',
      title: '90-Day Notice Lock & Buyout Discretion',
      clauseRef: 'Clause 8.1 — Termination of Employment & Notice',
      clauseExcerpt: 'Either party may terminate employment by giving 90 days notice in writing. Buyout of notice is solely at employer discretion.',
      severity: 'HIGH',
      whyItMatters: 'Discretionary buyout power rests entirely with Resource Management. Prospective employers in product/startup tiers frequently rescind offers demanding 30–45 day joiners.',
      financialImpact: 'Reduces lateral market mobility and eliminates negotiation leverage for future switches',
      verificationAction: 'Ask HR if early release via leave adjustment or buyout has written precedent in your project unit.',
      counterAmendment: 'Amend Clause 8.1: "Notice period to be 60 days, with employee having the unilateral right to buyout unserved notice at basic salary rate."',
    });
  } else if (noticePeriodDays >= 60) {
    risks.push({
      id: 'notice-period-60',
      category: 'Exit Mobility',
      title: '60-Day Notice Period',
      clauseRef: 'Clause 8.1 — Notice Period',
      clauseExcerpt: '60 days notice required upon voluntary resignation.',
      severity: 'MEDIUM',
      whyItMatters: 'Standard mid-tier notice period. Most product companies can accommodate 60 days with prompt knowledge transfer.',
      financialImpact: 'Moderate transition friction',
      verificationAction: 'Confirm buyout terms in appointment letter.',
      counterAmendment: 'No amendment necessary.',
    });
  } else {
    risks.push({
      id: 'notice-period-30',
      category: 'Exit Mobility',
      title: 'Agile 30-Day Notice Period',
      clauseRef: 'Clause 8.1 — Notice Period',
      clauseExcerpt: '30 days written notice required.',
      severity: 'CLEAN',
      whyItMatters: 'Fast 30-day notice allows rapid lateral hiring and peak market mobility.',
      financialImpact: 'Zero exit friction',
      verificationAction: 'Confirm 30-day notice applies equally to employee and employer.',
      counterAmendment: 'No amendment necessary.',
    });
  }

  return {
    quotedCtcLpa: ctcLpa,
    fixedCtcLpa: Math.round((fixedCtcRupees / 100000) * 100) / 100,
    variableLpa: Math.round((variableRupees / 100000) * 100) / 100,
    annualGratuityRupees,
    phantomGratuityLossRupees: phantomGratuityLoss,
    guaranteedYear1CashLpa,
    paperInflationGapRupees,
    paperInflationGapPct,
    risks,
  };
}
