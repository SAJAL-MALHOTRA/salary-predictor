export interface OfferInput {
  company: string;
  role: string;
  city: string;
  expYears: number;
  ctcLpa: number;
  variablePct: number;
  joiningBonusLpa: number;
  gratuityIncluded: boolean;
  variableFreq: 'Annual' | 'Quarterly';
  expectedTenureYears: number;
  noticePeriodDays: number;
}

export interface TakeHomeResult {
  ctcAnnual: number;
  basicAnnual: number;
  grossAnnual: number;
  epfAnnual: number;
  epfMonthly: number;
  ptAnnual: number;
  taxAnnual: number;
  taxMonthly: number;
  netAnnual: number;
  monthlyInHand: number;
}

export interface TaxRegimeComparison {
  newRegimeTax: number;
  newRegimeMonthlyInHand: number;
  oldRegimeTax: number;
  oldRegimeMonthlyInHand: number;
  hraExemption: number;
  totalDeductionsOld: number;
  betterRegime: 'NEW' | 'OLD';
  annualSavings: number;
  monthlySavings: number;
}

export interface StructuredRisk {
  id: string;
  category: string;
  title: string;
  clauseRef: string;
  clauseExcerpt: string;
  severity: 'HIGH' | 'MEDIUM' | 'CLEAN';
  whyItMatters: string;
  financialImpact: string;
  verificationAction: string;
  counterAmendment: string;
}

export interface ContractAuditResult {
  quotedCtcLpa: number;
  fixedCtcLpa: number;
  variableLpa: number;
  annualGratuityRupees: number;
  phantomGratuityLossRupees: number;
  guaranteedYear1CashLpa: number;
  paperInflationGapRupees: number;
  paperInflationGapPct: number;
  risks: StructuredRisk[];
}

export interface EquityModelResult {
  equityType: 'RSU' | 'ESOP';
  grantTotalLpa: number;
  vestSplits: number[];
  vestYearsLpa: number[];
  liquidityFactor: number;
  realizableYear1Lpa: number;
  perquisiteTaxYear1Lpa: number;
  exerciseWindowDays: number;
  exerciseTrapWarning?: string;
  totalYear1RewardsLpa: number;
}

export interface OfferProfile {
  id: string;
  name: string;
  company: string;
  role: string;
  ctcLpa: number;
  variablePct: number;
  joiningBonusLpa: number;
  noticePeriodDays: number;
  monthlyInHand: number;
  guaranteedCashLpa: number;
  tierNum: number;
  riskScore: number;
}

export interface RecruiterObjection {
  id: string;
  title: string;
  recruiterMotive: string;
  strategicLeverage: string;
  emailScript: string;
  verbalScript: string;
}
