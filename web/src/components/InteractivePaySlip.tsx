import React, { useState } from 'react';
import type { OfferInput, TakeHomeResult, ContractAuditResult } from '../types';
import { ArrowUpRight, AlertTriangle, Sparkles, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import confetti from 'canvas-confetti';

interface InteractivePaySlipProps {
  offer: OfferInput;
  setOffer: React.Dispatch<React.SetStateAction<OfferInput>>;
  takeHome: TakeHomeResult;
  audit: ContractAuditResult;
  onNavigateToTab: (tab: 'REDLINE' | 'TAX_OPTIMIZER' | 'COPILOT') => void;
}

export const InteractivePaySlip: React.FC<InteractivePaySlipProps> = ({
  offer,
  setOffer,
  takeHome,
  audit,
  onNavigateToTab
}) => {
  const [showItemized, setShowItemized] = useState(true);
  const [copiedMemo, setCopiedMemo] = useState(false);

  // Preset Handlers
  const handlePreset = (preset: { company: string; role: string; ctcLpa: number; variablePct: number; joiningBonusLpa: number; noticePeriodDays: number; tenure: number }) => {
    setOffer((prev) => ({
      ...prev,
      company: preset.company,
      role: preset.role,
      ctcLpa: preset.ctcLpa,
      variablePct: preset.variablePct,
      joiningBonusLpa: preset.joiningBonusLpa,
      noticePeriodDays: preset.noticePeriodDays,
      expectedTenureYears: preset.tenure
    }));
    confetti({
      particleCount: 40,
      spread: 60,
      origin: { y: 0.8 },
      colors: ['#4F46E5', '#10B981', '#6366F1']
    });
  };

  // Calculations for 3 Scenarios
  // Guaranteed = Fixed CTC minus gratuity loss (if tenure < 5y)
  const guaranteedMonthlyCash = Math.round(
    (audit.guaranteedYear1CashLpa * 100000 - takeHome.taxAnnual - takeHome.epfAnnual - takeHome.ptAnnual) / 12
  );
  // Expected = takeHome.monthlyInHand
  const expectedMonthlyCash = takeHome.monthlyInHand;
  // Max = 100% variable achieved + joining bonus distributed
  const maxYear1CashAnnual = takeHome.netAnnual + (audit.variableLpa * 100000 * 0.70) + (offer.joiningBonusLpa * 100000 * 0.688);
  const maxMonthlyCash = Math.round(maxYear1CashAnnual / 12);

  const copyExecutiveMemo = () => {
    const memo = `OFFER AUDIT INTELLIGENCE SUMMARY
Company: ${offer.company} | Role: ${offer.role}
Quoted CTC: ₹${offer.ctcLpa} LPA
Guaranteed Monthly In-Hand: ₹${guaranteedMonthlyCash.toLocaleString('en-IN')}
Expected Monthly In-Hand: ₹${expectedMonthlyCash.toLocaleString('en-IN')}
Maximum Monthly Potential: ₹${maxMonthlyCash.toLocaleString('en-IN')}
Paper CTC Inflation Gap: ₹${audit.paperInflationGapRupees.toLocaleString('en-IN')} (${audit.paperInflationGapPct}%)
Identified Contractual Risks: ${audit.risks.length} clauses flagged (Payment of Gratuity Act 1972, Clawback, Notice Lock).
Analyzed via Offer Intelligence Engine (Budget 2024 Compliant)`;

    navigator.clipboard.writeText(memo);
    setCopiedMemo(true);
    setTimeout(() => setCopiedMemo(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Quick Fill Preset Chips */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Example Offers:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handlePreset({ company: 'TCS', role: 'System Engineer', ctcLpa: 4.5, variablePct: 10, joiningBonusLpa: 0, noticePeriodDays: 90, tenure: 2 })}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              offer.company === 'TCS' ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-semibold' : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
            }`}
          >
            TCS (₹4.5L)
          </button>
          <button
            onClick={() => handlePreset({ company: 'Infosys', role: 'Senior Systems Engineer', ctcLpa: 12, variablePct: 15, joiningBonusLpa: 1.0, noticePeriodDays: 90, tenure: 2 })}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              offer.company === 'Infosys' ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-semibold' : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
            }`}
          >
            Infosys (₹12L)
          </button>
          <button
            onClick={() => handlePreset({ company: 'Swiggy', role: 'SDE II', ctcLpa: 24, variablePct: 15, joiningBonusLpa: 2.0, noticePeriodDays: 60, tenure: 2.5 })}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              offer.company === 'Swiggy' ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-semibold' : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
            }`}
          >
            Swiggy (₹24L)
          </button>
          <button
            onClick={() => handlePreset({ company: 'Google', role: 'Software Engineer III', ctcLpa: 35, variablePct: 15, joiningBonusLpa: 5.0, noticePeriodDays: 30, tenure: 3 })}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              offer.company === 'Google' ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-semibold' : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
            }`}
          >
            Google (₹35L)
          </button>
        </div>
      </div>

      {/* Main 2-Column Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Interactive Sliders & Offer Inputs */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
            <div className="border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">Offer Parameters</h2>
              <p className="text-xs text-slate-500">Fine-tune CTC components to observe real-time take-home changes.</p>
            </div>

            {/* Company & Role */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Company</label>
                <input
                  type="text"
                  value={offer.company}
                  onChange={(e) => setOffer({ ...offer, company: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Job Title</label>
                <input
                  type="text"
                  value={offer.role}
                  onChange={(e) => setOffer({ ...offer, role: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
                />
              </div>
            </div>

            {/* CTC Slider */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-xs font-semibold text-slate-700">Offered Annual CTC</label>
                <span className="text-sm font-bold text-indigo-600 font-mono">₹ {offer.ctcLpa.toFixed(1)} LPA</span>
              </div>
              <input
                type="range"
                min="3"
                max="80"
                step="0.5"
                value={offer.ctcLpa}
                onChange={(e) => setOffer({ ...offer, ctcLpa: parseFloat(e.target.value) })}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <div className="flex justify-between text-[11px] text-slate-400 mt-1">
                <span>₹3L</span>
                <span>₹25L</span>
                <span>₹50L</span>
                <span>₹80L</span>
              </div>
            </div>

            {/* Variable Pay Slider */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-xs font-semibold text-slate-700">Variable / Performance Pay</label>
                <span className="text-sm font-bold text-amber-600 font-mono">{offer.variablePct}% (₹{audit.variableLpa.toFixed(1)}L)</span>
              </div>
              <input
                type="range"
                min="0"
                max="40"
                step="1"
                value={offer.variablePct}
                onChange={(e) => setOffer({ ...offer, variablePct: parseInt(e.target.value) })}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
              />
              <div className="flex justify-between text-[11px] text-slate-400 mt-1">
                <span>0% (All Fixed)</span>
                <span>15% (Typical)</span>
                <span>40% (High Risk)</span>
              </div>
            </div>

            {/* Joining Bonus & Notice Period */}
            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Joining Bonus</label>
                <div className="relative">
                  <span className="absolute left-3 top-2 text-xs text-slate-400">₹</span>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    max="20"
                    value={offer.joiningBonusLpa}
                    onChange={(e) => setOffer({ ...offer, joiningBonusLpa: parseFloat(e.target.value) || 0 })}
                    className="w-full pl-6 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                  />
                  <span className="absolute right-3 top-2 text-xs text-slate-400">LPA</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Notice Period</label>
                <select
                  value={offer.noticePeriodDays}
                  onChange={(e) => setOffer({ ...offer, noticePeriodDays: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
                >
                  <option value={30}>30 Days (Agile)</option>
                  <option value={60}>60 Days (Standard)</option>
                  <option value={90}>90 Days (Lock-in)</option>
                </select>
              </div>
            </div>

            {/* Gratuity Checkbox & Expected Tenure */}
            <div className="pt-2 border-t border-slate-100 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="gratuityIncluded"
                    checked={offer.gratuityIncluded}
                    onChange={(e) => setOffer({ ...offer, gratuityIncluded: e.target.checked })}
                    className="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                  />
                  <label htmlFor="gratuityIncluded" className="text-xs font-semibold text-slate-700 cursor-pointer">
                    Gratuity deducted inside CTC
                  </label>
                </div>
                <span className="text-[11px] font-mono text-slate-500">₹ {audit.annualGratuityRupees.toLocaleString('en-IN')}/yr</span>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-semibold text-slate-700">Planned Tenure at Company</label>
                  <span className="text-xs font-bold text-slate-700 font-mono">{offer.expectedTenureYears} Years</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="6"
                  step="0.5"
                  value={offer.expectedTenureYears}
                  onChange={(e) => setOffer({ ...offer, expectedTenureYears: parseFloat(e.target.value) })}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-700"
                />
                <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                  <span>1 yr</span>
                  <span className="text-rose-600 font-medium">&lt; 5 yrs: 100% Forfeited</span>
                  <span className="text-emerald-600 font-medium">&ge; 5 yrs: Vested</span>
                </div>
              </div>
            </div>
          </div>

          {/* Paper CTC Inflation Metric Banner */}
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-amber-100 rounded-lg text-amber-800">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-amber-900">CTC Inflation Gap: ₹ {audit.paperInflationGapRupees.toLocaleString('en-IN')}</h4>
                  <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-200 text-amber-900">
                    {audit.paperInflationGapPct}% Phantom
                  </span>
                </div>
                <p className="text-xs text-amber-800 leading-relaxed">
                  Only <strong>₹ {audit.guaranteedYear1CashLpa} LPA</strong> is contractually guaranteed in Year 1.
                  The remaining ₹ {(audit.paperInflationGapRupees / 100000).toFixed(1)} Lakhs consists of contingent variable pay and statutory gratuity allocations.
                </p>
                <div className="pt-2">
                  <button
                    onClick={() => onNavigateToTab('REDLINE')}
                    className="inline-flex items-center gap-1 text-xs font-bold text-amber-900 hover:text-amber-950 underline"
                  >
                    View redlined contract clauses <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Executive Take-Home & Breakdown */}
        <div className="lg:col-span-7 space-y-6">
          {/* Executive Compensation Card */}
          <div className="bg-slate-900 text-white p-7 rounded-2xl shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-5">
              <div>
                <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Estimated Monthly Net In-Hand</span>
                <div className="text-4xl font-extrabold font-mono tracking-tight text-white mt-1">
                  ₹ {takeHome.monthlyInHand.toLocaleString('en-IN')}
                  <span className="text-sm font-normal text-slate-400 ml-2">/ month</span>
                </div>
              </div>
              <button
                onClick={copyExecutiveMemo}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all border border-slate-700"
              >
                {copiedMemo ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedMemo ? 'Copied Summary' : 'Copy Executive Memo'}</span>
              </button>
            </div>

            {/* 3 Metric Floors */}
            <div className="grid grid-cols-3 gap-3 pt-1">
              <div className="bg-slate-800/70 p-3.5 rounded-xl border border-slate-700/60">
                <span className="text-[11px] font-medium text-rose-400 uppercase tracking-wide block">Guaranteed Floor</span>
                <span className="text-lg font-bold font-mono text-white mt-1 block">
                  ₹ {guaranteedMonthlyCash.toLocaleString('en-IN')}
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">0% variable payout</span>
              </div>

              <div className="bg-slate-800/70 p-3.5 rounded-xl border border-indigo-500/40 relative">
                <span className="text-[11px] font-medium text-indigo-300 uppercase tracking-wide block">Expected Payout</span>
                <span className="text-lg font-bold font-mono text-white mt-1 block">
                  ₹ {expectedMonthlyCash.toLocaleString('en-IN')}
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">{offer.variablePct}% var assumed</span>
              </div>

              <div className="bg-slate-800/70 p-3.5 rounded-xl border border-emerald-500/30">
                <span className="text-[11px] font-medium text-emerald-400 uppercase tracking-wide block">Maximum Potential</span>
                <span className="text-lg font-bold font-mono text-white mt-1 block">
                  ₹ {maxMonthlyCash.toLocaleString('en-IN')}
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">100% var + bonus</span>
              </div>
            </div>
          </div>

          {/* Scenario Comparison Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Compensation Scenarios</h3>
                <p className="text-xs text-slate-500">Contractual certainty vs performance contingency</p>
              </div>
              <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full border border-indigo-100">
                FY 2024-25
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-50 text-slate-600 border-b border-slate-200">
                    <th className="py-3 px-4 font-semibold">Scenario</th>
                    <th className="py-3 px-4 font-semibold">Condition</th>
                    <th className="py-3 px-4 font-semibold text-right">Annual Net Cash</th>
                    <th className="py-3 px-4 font-semibold text-right">Monthly Bank Credit</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr className="hover:bg-slate-50/60">
                    <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                      Guaranteed Floor
                    </td>
                    <td className="py-3 px-4 text-slate-500">Zero variable pay realized + tenure &lt; 5 yrs</td>
                    <td className="py-3 px-4 font-mono font-medium text-right text-slate-800">
                      ₹ {(guaranteedMonthlyCash * 12).toLocaleString('en-IN')}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-right text-slate-900">
                      ₹ {guaranteedMonthlyCash.toLocaleString('en-IN')}
                    </td>
                  </tr>

                  <tr className="bg-indigo-50/40 hover:bg-indigo-50/70">
                    <td className="py-3 px-4 font-bold text-indigo-950 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-indigo-600"></span>
                      Expected Baseline
                    </td>
                    <td className="py-3 px-4 text-slate-600">{offer.variablePct}% target variable payout</td>
                    <td className="py-3 px-4 font-mono font-medium text-right text-indigo-950">
                      ₹ {takeHome.netAnnual.toLocaleString('en-IN')}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-right text-indigo-600">
                      ₹ {expectedMonthlyCash.toLocaleString('en-IN')}
                    </td>
                  </tr>

                  <tr className="hover:bg-slate-50/60">
                    <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                      Maximum Ceiling
                    </td>
                    <td className="py-3 px-4 text-slate-500">100% variable achieved + sign-on bonus</td>
                    <td className="py-3 px-4 font-mono font-medium text-right text-slate-800">
                      ₹ {maxYear1CashAnnual.toLocaleString('en-IN')}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-right text-emerald-600">
                      ₹ {maxMonthlyCash.toLocaleString('en-IN')}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Itemized Salary Breakdown (Expandable) */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <button
              onClick={() => setShowItemized(!showItemized)}
              className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-slate-50/80 transition-all"
            >
              <div>
                <h3 className="text-sm font-bold text-slate-900">Itemized Monthly Pay Slip Breakdown</h3>
                <p className="text-xs text-slate-500">Transparent deduction and taxation mechanics</p>
              </div>
              <div className="flex items-center gap-2 text-slate-500 text-xs">
                <span>{showItemized ? 'Hide' : 'Expand'}</span>
                {showItemized ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </button>

            {showItemized && (
              <div className="px-6 pb-6 pt-2 border-t border-slate-100">
                <div className="space-y-2.5">
                  <div className="flex justify-between items-center text-xs py-1 border-b border-slate-100">
                    <span className="text-slate-600 font-medium">Basic Salary (40% of CTC)</span>
                    <span className="font-mono font-semibold text-slate-900">
                      ₹ {Math.round(takeHome.basicAnnual / 12).toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-xs py-1 border-b border-slate-100">
                    <span className="text-slate-600 font-medium">HRA & Special Allowances</span>
                    <span className="font-mono font-semibold text-slate-900">
                      ₹ {Math.round((takeHome.grossAnnual - takeHome.basicAnnual) / 12).toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-xs py-1 text-slate-800 font-bold bg-slate-50 px-2 rounded">
                    <span>Gross Fixed Earnings</span>
                    <span className="font-mono">
                      ₹ {Math.round(takeHome.grossAnnual / 12).toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-xs py-1 border-b border-slate-100 text-rose-700">
                    <span className="font-medium">Employee PF (12% of basic, capped)</span>
                    <span className="font-mono font-semibold">
                      - ₹ {Math.round(takeHome.epfMonthly).toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-xs py-1 border-b border-slate-100 text-rose-700">
                    <span className="font-medium">Professional Tax (PT)</span>
                    <span className="font-mono font-semibold">
                      - ₹ {Math.round(takeHome.ptAnnual / 12).toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-xs py-1 border-b border-slate-100 text-rose-700">
                    <span className="font-medium">Estimated Monthly TDS (New Regime)</span>
                    <span className="font-mono font-semibold">
                      - ₹ {Math.round(takeHome.taxMonthly).toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-sm py-2 bg-emerald-50 text-emerald-900 font-extrabold px-3 rounded-lg mt-2">
                    <span>Net Take-Home Bank Credit</span>
                    <span className="font-mono text-base">
                      ₹ {takeHome.monthlyInHand.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <span>Paying rent in Bangalore or Mumbai?</span>
                  <button
                    onClick={() => onNavigateToTab('TAX_OPTIMIZER')}
                    className="text-indigo-600 font-bold hover:underline flex items-center gap-1"
                  >
                    Compare Old vs New Tax Regime <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
