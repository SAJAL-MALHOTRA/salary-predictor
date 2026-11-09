import React, { useState } from 'react';
import type { OfferInput } from '../types';
import { compareTaxRegimes } from '../lib/taxEngine';
import { Scale, Home, AlertCircle } from 'lucide-react';

interface OldVsNewTaxOptimizerProps {
  offer: OfferInput;
}

export const OldVsNewTaxOptimizer: React.FC<OldVsNewTaxOptimizerProps> = ({ offer }) => {
  const [monthlyRent, setMonthlyRent] = useState<number>(28000);
  const [isMetro, setIsMetro] = useState<boolean>(true);
  const [sec80c, setSec80c] = useState<number>(150000);
  const [sec80d, setSec80d] = useState<number>(25000);
  const [nps, setNps] = useState<number>(50000);

  const comparison = compareTaxRegimes(
    offer.ctcLpa,
    monthlyRent,
    isMetro,
    sec80c,
    sec80d,
    nps
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Old vs New Tax Regime Rupee Optimizer</h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              Budget 2024 Slabs
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Section 10(13A) Metro HRA Exemption, Section 80C, 80D, and NPS 80CCD(1B) optimization for ₹ {offer.ctcLpa} LPA CTC.
          </p>
        </div>

        {/* Savings Winner Badge */}
        <div className={`p-4 rounded-xl border flex items-center gap-3 ${
          comparison.betterRegime === 'OLD'
            ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
            : 'bg-indigo-50 border-indigo-200 text-indigo-900'
        }`}>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-base ${
            comparison.betterRegime === 'OLD' ? 'bg-emerald-600 text-white' : 'bg-indigo-600 text-white'
          }`}>
            {comparison.betterRegime}
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider block">Recommended Regime</span>
            <div className="text-base font-extrabold font-mono">
              Save ₹ {comparison.annualSavings.toLocaleString('en-IN')}/yr
              <span className="text-xs font-normal opacity-80 ml-1">
                (₹ {comparison.monthlySavings.toLocaleString('en-IN')}/mo)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 2-Column Layout: Deduction Sliders (Left) & Side-by-Side Comparison (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Rent & Chapter VI-A Deduction Sliders */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Home className="w-4 h-4 text-indigo-600" />
              <span>HRA & Tax Deductions (Old Regime)</span>
            </h3>
            <p className="text-xs text-slate-500">Tune rent and investments to find your regime crossover point.</p>
          </div>

          {/* Monthly Rent Slider */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-semibold text-slate-700">Monthly House Rent Paid</label>
              <span className="text-sm font-bold text-indigo-600 font-mono">₹ {monthlyRent.toLocaleString('en-IN')} / mo</span>
            </div>
            <input
              type="range"
              min="0"
              max="75000"
              step="1000"
              value={monthlyRent}
              onChange={(e) => setMonthlyRent(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <div className="flex justify-between text-[11px] text-slate-400 mt-1">
              <span>₹0</span>
              <span>₹25,000 (Bangalore Avg)</span>
              <span>₹75,000</span>
            </div>
          </div>

          {/* Metro Toggle */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
            <div>
              <span className="text-xs font-bold text-slate-800 block">Metro City HRA Allowance</span>
              <span className="text-[11px] text-slate-500">Mumbai, Delhi, Kolkata, Chennai (50% basic) vs Others (40%)</span>
            </div>
            <button
              onClick={() => setIsMetro(!isMetro)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                isMetro ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-700'
              }`}
            >
              {isMetro ? 'Metro (50%)' : 'Non-Metro (40%)'}
            </button>
          </div>

          {/* Section 80C Slider */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-semibold text-slate-700">Section 80C (EPF, ELSS, PPF)</label>
              <span className="text-sm font-bold text-slate-800 font-mono">₹ {sec80c.toLocaleString('en-IN')}</span>
            </div>
            <input
              type="range"
              min="0"
              max="150000"
              step="5000"
              value={sec80c}
              onChange={(e) => setSec80c(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-700"
            />
            <div className="flex justify-between text-[11px] text-slate-400 mt-1">
              <span>₹0</span>
              <span>₹75,000</span>
              <span>₹1,50,000 (Max Cap)</span>
            </div>
          </div>

          {/* Section 80D Slider */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-semibold text-slate-700">Section 80D (Health Insurance)</label>
              <span className="text-sm font-bold text-slate-800 font-mono">₹ {sec80d.toLocaleString('en-IN')}</span>
            </div>
            <input
              type="range"
              min="0"
              max="75000"
              step="5000"
              value={sec80d}
              onChange={(e) => setSec80d(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-700"
            />
            <div className="flex justify-between text-[11px] text-slate-400 mt-1">
              <span>₹0</span>
              <span>₹25,000 (Self)</span>
              <span>₹75,000 (Parents)</span>
            </div>
          </div>

          {/* NPS Section 80CCD(1B) Slider */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-semibold text-slate-700">NPS Tier 1 [Section 80CCD(1B)]</label>
              <span className="text-sm font-bold text-slate-800 font-mono">₹ {nps.toLocaleString('en-IN')}</span>
            </div>
            <input
              type="range"
              min="0"
              max="50000"
              step="5000"
              value={nps}
              onChange={(e) => setNps(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-700"
            />
            <div className="flex justify-between text-[11px] text-slate-400 mt-1">
              <span>₹0</span>
              <span>₹25,000</span>
              <span>₹50,000 (Max Cap)</span>
            </div>
          </div>
        </div>

        {/* Right Column: Comparative Analysis & Deduction Breakdown Table */}
        <div className="lg:col-span-7 space-y-6">
          {/* Side by Side Cards */}
          <div className="grid grid-cols-2 gap-4">
            {/* New Regime Card */}
            <div className={`p-5 rounded-2xl border transition-all ${
              comparison.betterRegime === 'NEW'
                ? 'bg-indigo-50/70 border-indigo-400 ring-2 ring-indigo-200 shadow-md'
                : 'bg-white border-slate-200 shadow-sm'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-600">New Regime (Default)</span>
                {comparison.betterRegime === 'NEW' && (
                  <span className="px-2 py-0.5 text-[10px] font-extrabold bg-indigo-600 text-white rounded-full">
                    OPTIMAL
                  </span>
                )}
              </div>
              <div className="text-2xl font-black font-mono text-slate-900">
                ₹ {comparison.newRegimeMonthlyInHand.toLocaleString('en-IN')}
                <span className="text-xs font-normal text-slate-500 ml-1">/mo</span>
              </div>
              <div className="mt-3 text-xs text-slate-600 space-y-1">
                <div className="flex justify-between">
                  <span>Annual Tax:</span>
                  <span className="font-mono font-bold">₹ {comparison.newRegimeTax.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between">
                  <span>Standard Deduction:</span>
                  <span className="font-mono font-medium">₹ 75,000</span>
                </div>
              </div>
            </div>

            {/* Old Regime Card */}
            <div className={`p-5 rounded-2xl border transition-all ${
              comparison.betterRegime === 'OLD'
                ? 'bg-emerald-50/70 border-emerald-400 ring-2 ring-emerald-200 shadow-md'
                : 'bg-white border-slate-200 shadow-sm'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-600">Old Regime (Exemptions)</span>
                {comparison.betterRegime === 'OLD' && (
                  <span className="px-2 py-0.5 text-[10px] font-extrabold bg-emerald-600 text-white rounded-full">
                    OPTIMAL
                  </span>
                )}
              </div>
              <div className="text-2xl font-black font-mono text-slate-900">
                ₹ {comparison.oldRegimeMonthlyInHand.toLocaleString('en-IN')}
                <span className="text-xs font-normal text-slate-500 ml-1">/mo</span>
              </div>
              <div className="mt-3 text-xs text-slate-600 space-y-1">
                <div className="flex justify-between">
                  <span>Annual Tax:</span>
                  <span className="font-mono font-bold">₹ {comparison.oldRegimeTax.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between">
                  <span>Total Deductions:</span>
                  <span className="font-mono font-medium">₹ {comparison.totalDeductionsOld.toLocaleString('en-IN')}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Statutory Comparison Matrix */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-900">Statutory Exemption Breakdown</h4>
                <p className="text-xs text-slate-500">Legal Section 10(13A) and Chapter VI-A comparison</p>
              </div>
              <span className="text-xs font-mono text-slate-600">CTC: ₹ {offer.ctcLpa} LPA</span>
            </div>

            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 text-slate-600 border-b border-slate-200">
                  <th className="py-3 px-4 font-semibold">Exemption / Deduction</th>
                  <th className="py-3 px-4 font-semibold text-right">New Regime</th>
                  <th className="py-3 px-4 font-semibold text-right">Old Regime</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                <tr>
                  <td className="py-2.5 px-4 font-sans text-slate-700">Standard Deduction</td>
                  <td className="py-2.5 px-4 text-right text-indigo-600 font-semibold">₹ 75,000</td>
                  <td className="py-2.5 px-4 text-right text-slate-800">₹ 50,000</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-sans text-slate-700">HRA Exemption u/s 10(13A)</td>
                  <td className="py-2.5 px-4 text-right text-slate-400">₹ 0 (Not allowed)</td>
                  <td className="py-2.5 px-4 text-right text-emerald-600 font-semibold">₹ {comparison.hraExemption.toLocaleString('en-IN')}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-sans text-slate-700">Section 80C (EPF + ELSS)</td>
                  <td className="py-2.5 px-4 text-right text-slate-400">₹ 0</td>
                  <td className="py-2.5 px-4 text-right text-slate-800">₹ {sec80c.toLocaleString('en-IN')}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-sans text-slate-700">Section 80D (Health Insurance)</td>
                  <td className="py-2.5 px-4 text-right text-slate-400">₹ 0</td>
                  <td className="py-2.5 px-4 text-right text-slate-800">₹ {sec80d.toLocaleString('en-IN')}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-sans text-slate-700">NPS 80CCD(1B)</td>
                  <td className="py-2.5 px-4 text-right text-slate-400">₹ 0</td>
                  <td className="py-2.5 px-4 text-right text-slate-800">₹ {nps.toLocaleString('en-IN')}</td>
                </tr>
                <tr className="bg-slate-50 font-bold">
                  <td className="py-3 px-4 font-sans text-slate-900">Total Tax Deductions Claimed</td>
                  <td className="py-3 px-4 text-right text-slate-900">₹ 75,000</td>
                  <td className="py-3 px-4 text-right text-emerald-700">₹ {comparison.totalDeductionsOld.toLocaleString('en-IN')}</td>
                </tr>
                <tr className="bg-slate-100/60 font-black">
                  <td className="py-3 px-4 font-sans text-slate-900">Annual Tax Payable</td>
                  <td className="py-3 px-4 text-right text-slate-900">₹ {comparison.newRegimeTax.toLocaleString('en-IN')}</td>
                  <td className="py-3 px-4 text-right text-slate-900">₹ {comparison.oldRegimeTax.toLocaleString('en-IN')}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Practical Filing Advice */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
            <p className="text-xs text-slate-600 leading-relaxed">
              <strong>Filing Strategy:</strong> You can select the New Regime with your employer payroll team for lower initial monthly TDS deductions, and still switch to the Old Regime when filing your ITR (Form 1) if your aggregate rent receipts and Section 80C declarations maximize tax refunds.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
