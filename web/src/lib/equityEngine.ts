import type { EquityModelResult } from '../types';

export function evaluateEquityGrant(
  equityType: 'RSU' | 'ESOP',
  grantValueLpa: number = 24.0,
  vestingSchedule: 'Standard 25/25/25/25' | 'Amazon 5/15/40/40' | 'Frontloaded 33/33/22/12' = 'Standard 25/25/25/25',
  companyStage: 'Public Listed Tech' | 'Late-Stage Unicorn' | 'Early-Stage Startup' = 'Public Listed Tech',
  exerciseWindowDays: number = 90,
  baseCtcLpa: number = 20.0
): EquityModelResult {
  const grantTotal = Math.max(0, grantValueLpa);

  let vestSplits = [0.25, 0.25, 0.25, 0.25];
  if (vestingSchedule === 'Amazon 5/15/40/40') {
    vestSplits = [0.05, 0.15, 0.40, 0.40];
  } else if (vestingSchedule === 'Frontloaded 33/33/22/12') {
    vestSplits = [0.33, 0.33, 0.22, 0.12];
  }

  const vestYearsLpa = vestSplits.map((split) => Math.round(grantTotal * split * 100) / 100);
  const y1VestLpa = vestYearsLpa[0];

  // Liquidity Haircut Factor
  let liquidityFactor = 1.0;
  if (equityType === 'ESOP') {
    if (companyStage === 'Late-Stage Unicorn') {
      liquidityFactor = 0.65;
    } else {
      liquidityFactor = 0.30;
    }
  }

  const realizableYear1Lpa = Math.round(y1VestLpa * liquidityFactor * 100) / 100;
  const perquisiteTaxYear1Lpa = Math.round(y1VestLpa * 0.312 * 100) / 100;

  let exerciseTrapWarning: string | undefined;
  if (equityType === 'ESOP' && exerciseWindowDays <= 90) {
    exerciseTrapWarning = `⚠️ 90-Day Golden Handcuffs Trap: Departing requires exercising all vested options within ${exerciseWindowDays} days. Because the company is unlisted, you must pay both the strike price AND perquisite tax out-of-pocket in cash or surrender 100% of your earned equity.`;
  }

  const totalYear1RewardsLpa = Math.round((baseCtcLpa + realizableYear1Lpa) * 100) / 100;

  return {
    equityType,
    grantTotalLpa: grantTotal,
    vestSplits,
    vestYearsLpa,
    liquidityFactor,
    realizableYear1Lpa,
    perquisiteTaxYear1Lpa,
    exerciseWindowDays,
    exerciseTrapWarning,
    totalYear1RewardsLpa,
  };
}
