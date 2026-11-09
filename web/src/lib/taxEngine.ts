import type { TakeHomeResult, TaxRegimeComparison } from '../types';

/**
 * Budget 2024 New Tax Regime (FY 2024-25, AY 2025-26)
 * Standard Deduction: ₹75,000. Basic assumed at 40% of CTC.
 */
export function calculateTakeHomeNewRegime(ctcLpa: number): TakeHomeResult {
  const ctc = Math.max(0, ctcLpa) * 100000;
  const basic = ctc * 0.40;

  // EPF: 12% of basic (statutory cap at ₹1,800/mo if basic*0.12 > 1800*12 and CTC > 15L)
  let epfAnnual: number;
  if (basic * 0.12 > 1800 * 12 && ctc > 1500000) {
    epfAnnual = 1800 * 12;
  } else {
    epfAnnual = basic * 0.12;
  }

  const grossSalary = ctc - epfAnnual;
  const ptAnnual = ctc >= 300000 ? 2400 : 0;

  // Standard deduction ₹75,000 under Budget 2024 New Regime
  const taxableIncome = Math.max(0, grossSalary - 75000);
  let tax = 0;

  // Slabs:
  // 0 - 3L: Nil
  // 3L - 7L: 5% (with rebate u/s 87A up to 7L taxable income = 0)
  // 7L - 10L: 10%
  // 10L - 12L: 15%
  // 12L - 15L: 20%
  // Above 15L: 30%
  if (taxableIncome > 700000) {
    if (taxableIncome > 1500000) {
      tax += (taxableIncome - 1500000) * 0.30;
      tax += 300000 * 0.20;
      tax += 200000 * 0.15;
      tax += 300000 * 0.10;
      tax += 400000 * 0.05;
    } else if (taxableIncome > 1200000) {
      tax += (taxableIncome - 1200000) * 0.20;
      tax += 200000 * 0.15;
      tax += 300000 * 0.10;
      tax += 400000 * 0.05;
    } else if (taxableIncome > 1000000) {
      tax += (taxableIncome - 1000000) * 0.15;
      tax += 300000 * 0.10;
      tax += 400000 * 0.05;
    } else if (taxableIncome > 700000) {
      tax += (taxableIncome - 700000) * 0.10;
      tax += 400000 * 0.05;
    }
    tax *= 1.04; // 4% Health & Education Cess
  }

  const netAnnual = grossSalary - epfAnnual - ptAnnual - tax;
  const monthlyInHand = netAnnual / 12;

  return {
    ctcAnnual: ctc,
    basicAnnual: basic,
    grossAnnual: grossSalary,
    epfAnnual,
    epfMonthly: epfAnnual / 12,
    ptAnnual,
    taxAnnual: Math.round(tax),
    taxMonthly: Math.round(tax / 12),
    netAnnual: Math.round(netAnnual),
    monthlyInHand: Math.round(monthlyInHand),
  };
}

/**
 * Old Tax Regime Calculation with HRA & Common Chapter VI-A Deductions
 */
export function calculateTakeHomeOldRegime(
  ctcLpa: number,
  monthlyRent: number = 25000,
  isMetro: boolean = true,
  sec80c: number = 150000,
  sec80d: number = 25000,
  nps80ccd1b: number = 50000
): { taxAnnual: number; monthlyInHand: number; hraExemption: number; totalDeductions: number } {
  const ctc = Math.max(0, ctcLpa) * 100000;
  const basic = ctc * 0.40;

  // EPF
  const epfAnnual = basic * 0.12 > 1800 * 12 && ctc > 1500000 ? 1800 * 12 : basic * 0.12;
  const grossSalary = ctc - epfAnnual;
  const ptAnnual = ctc >= 300000 ? 2400 : 0;

  // HRA Exemption u/s 10(13A):
  // Minimum of:
  // 1. Actual HRA received (assume 50% of basic in metro, 40% non-metro)
  // 2. Rent paid minus 10% of basic
  // 3. 50% (metro) or 40% (non-metro) of basic
  const actualHra = basic * (isMetro ? 0.50 : 0.40);
  const totalRentPaidAnnual = monthlyRent * 12;
  const rentMinusTenPctBasic = Math.max(0, totalRentPaidAnnual - basic * 0.10);
  const metroPctBasic = basic * (isMetro ? 0.50 : 0.40);

  const hraExemption = Math.min(actualHra, rentMinusTenPctBasic, metroPctBasic);

  // Deductions:
  // Standard Deduction: ₹50,000 under Old Regime
  // Professional Tax: ₹2,400
  // 80C capped at ₹1,50,000 (includes EPF)
  const effective80c = Math.min(150000, Math.max(sec80c, epfAnnual));
  const effective80d = Math.min(75000, sec80d);
  const effectiveNps = Math.min(50000, nps80ccd1b);

  const totalDeductions = 50000 + ptAnnual + hraExemption + effective80c + effective80d + effectiveNps;
  const taxableIncome = Math.max(0, grossSalary - totalDeductions);

  let tax = 0;
  // Old Slabs:
  // 0 - 2.5L: Nil
  // 2.5L - 5L: 5% (Rebate 87A if taxable income <= 5L)
  // 5L - 10L: 20%
  // Above 10L: 30%
  if (taxableIncome > 500000) {
    if (taxableIncome > 1000000) {
      tax += (taxableIncome - 1000000) * 0.30;
      tax += 500000 * 0.20;
      tax += 250000 * 0.05;
    } else {
      tax += (taxableIncome - 500000) * 0.20;
      tax += 250000 * 0.05;
    }
    tax *= 1.04; // 4% Cess
  }

  const netAnnual = grossSalary - epfAnnual - ptAnnual - tax;
  const monthlyInHand = netAnnual / 12;

  return {
    taxAnnual: Math.round(tax),
    monthlyInHand: Math.round(monthlyInHand),
    hraExemption: Math.round(hraExemption),
    totalDeductions: Math.round(totalDeductions),
  };
}

/**
 * Compare New vs Old Tax Regime to find exact savings crossover
 */
export function compareTaxRegimes(
  ctcLpa: number,
  monthlyRent: number = 25000,
  isMetro: boolean = true,
  sec80c: number = 150000,
  sec80d: number = 25000,
  nps80ccd1b: number = 50000
): TaxRegimeComparison {
  const newRes = calculateTakeHomeNewRegime(ctcLpa);
  const oldRes = calculateTakeHomeOldRegime(ctcLpa, monthlyRent, isMetro, sec80c, sec80d, nps80ccd1b);

  const newTax = newRes.taxAnnual;
  const oldTax = oldRes.taxAnnual;

  const betterRegime = oldTax < newTax ? 'OLD' : 'NEW';
  const annualSavings = Math.abs(newTax - oldTax);
  const monthlySavings = Math.round(annualSavings / 12);

  return {
    newRegimeTax: newTax,
    newRegimeMonthlyInHand: newRes.monthlyInHand,
    oldRegimeTax: oldTax,
    oldRegimeMonthlyInHand: oldRes.monthlyInHand,
    hraExemption: oldRes.hraExemption,
    totalDeductionsOld: oldRes.totalDeductions,
    betterRegime,
    annualSavings,
    monthlySavings,
  };
}
