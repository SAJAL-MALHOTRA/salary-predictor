import React, { useState } from 'react';
import type { OfferInput } from '../types';
import { evaluateEquityGrant } from '../lib/equityEngine';
import { TrendingUp, AlertTriangle, Lock } from 'lucide-react';

interface EquityValuationModelerProps {
  offer: OfferInput;
}

export const EquityValuationModeler: React.FC<EquityValuationModelerProps> = ({ offer }) => {
  const [equityType, setEquityType] = useState<'RSU' | 'ESOP'>('ESOP');
  const [grantValueLpa, setGrantValueLpa] = useState<number>(24.0);
  const [vestingSchedule, setVestingSchedule] = useState<'Standard 25/25/25/25' | 'Amazon 5/15/40/40' | 'Frontloaded 33/33/22/12'>('Standard 25/25/25/25');
  const [companyStage, setCompanyStage] = useState<'Public Listed Tech' | 'Late-Stage Unicorn' | 'Early-Stage Startup'>('Late-Stage Unicorn');
  const [exerciseWindowDays, setExerciseWindowDays] = useState<number>(90);

  const equityResult = evaluateEquityGrant(
    equityType,
    grantValueLpa,
    vestingSchedule,
    companyStage,
    exerciseWindowDays,
    offer.ctcLpa
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Equity & ESOP Valuation Modeler</h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
              Indian Tax & Liquidity Engine
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Simulate 4-year vesting schedules, unlisted liquidity discounts, Section 17(2) perquisite tax, and the 90-day exercise trap.
          </p>
        </div>

        {/* Total Realizable Year-1 Rewards Card */}
        <div className="p-4 rounded-xl bg-slate-900 text-white flex items-center gap-3">
          <div>
            <span className="text-[11px] font-medium uppercase text-slate-400 block">Total Year 1 Compensation (Cash + Equity)</span>
            <div className="text-lg font-black font-mono text-emerald-400">
              ₹ {equityResult.totalYear1RewardsLpa.toFixed(1)} LPA
              <span className="text-xs font-normal text-slate-400 ml-1.5">
                (₹ {offer.ctcLpa}L Cash + ₹ {equityResult.realizableYear1Lpa}L Equity)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 2-Column Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Input Controls */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900">Grant Details</h3>
            <p className="text-xs text-slate-500">Configure equity vehicle, vesting curve, and exit liquidity.</p>
          </div>

          {/* Equity Type Toggle */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Equity Vehicle</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => { setEquityType('RSU'); setCompanyStage('Public Listed Tech'); }}
                className={`py-2 text-xs font-bold rounded-lg border transition-all ${
                  equityType === 'RSU' ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-slate-50 text-slate-700 border-slate-200'
                }`}
              >
                RSU (Public Tech)
              </button>
              <button
                onClick={() => { setEquityType('ESOP'); setCompanyStage('Late-Stage Unicorn'); }}
                className={`py-2 text-xs font-bold rounded-lg border transition-all ${
                  equityType === 'ESOP' ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-slate-50 text-slate-700 border-slate-200'
                }`}
              >
                ESOP (Startup / Unicorn)
              </button>
            </div>
          </div>

          {/* Total Grant Value Slider */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-semibold text-slate-700">4-Year Total Grant Value</label>
              <span className="text-sm font-bold text-indigo-600 font-mono">₹ {grantValueLpa.toFixed(1)} LPA</span>
            </div>
            <input
              type="range"
              min="0"
              max="80"
              step="1"
              value={grantValueLpa}
              onChange={(e) => setGrantValueLpa(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <div className="flex justify-between text-[11px] text-slate-400 mt-1">
              <span>₹0</span>
              <span>₹20L</span>
              <span>₹50L</span>
              <span>₹80L</span>
            </div>
          </div>

          {/* Vesting Curve Schedule */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Vesting Schedule</label>
            <select
              value={vestingSchedule}
              onChange={(e: any) => setVestingSchedule(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
            >
              <option value="Standard 25/25/25/25">Standard: 25% / 25% / 25% / 25% (Equal 4y)</option>
              <option value="Amazon 5/15/40/40">Amazon-style: 5% / 15% / 40% / 40% (Backloaded)</option>
              <option value="Frontloaded 33/33/22/12">Frontloaded: 33% / 33% / 22% / 12%</option>
            </select>
          </div>

          {/* Company Stage */}
          {equityType === 'ESOP' && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Company Liquidity Stage</label>
              <select
                value={companyStage}
                onChange={(e: any) => setCompanyStage(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
              >
                <option value="Late-Stage Unicorn">Late-Stage Unicorn (65% Realizability / Buybacks)</option>
                <option value="Early-Stage Startup">Early-Stage Startup (30% Realizability / High Risk)</option>
              </select>
            </div>
          )}

          {/* Exercise Window */}
          {equityType === 'ESOP' && (
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-semibold text-slate-700">Post-Termination Exercise Window</label>
                <span className={`text-xs font-mono font-bold ${exerciseWindowDays <= 90 ? 'text-rose-600' : 'text-emerald-600'}`}>
                  {exerciseWindowDays} Days
                </span>
              </div>
              <input
                type="range"
                min="30"
                max="365"
                step="30"
                value={exerciseWindowDays}
                onChange={(e) => setExerciseWindowDays(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-700"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span className="text-rose-600 font-medium">90d (Trap)</span>
                <span>180d</span>
                <span className="text-emerald-600 font-medium">365d+ (Fair)</span>
              </div>
            </div>
          )}
        </div>

        {/* Right: 4-Year Vesting Visualization & Indian Tax Warnings */}
        <div className="lg:col-span-7 space-y-6">
          {/* 4-Year Vesting Schedule Cards */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold text-slate-900">4-Year Realizable Vesting Timeline</h3>
              <span className="text-xs font-mono text-slate-500">
                Liquidity Haircut: {Math.round((1 - equityResult.liquidityFactor) * 100)}%
              </span>
            </div>

            <div className="grid grid-cols-4 gap-3 pt-2">
              {equityResult.vestYearsLpa.map((vestAmount, index) => {
                const realizable = Math.round(vestAmount * equityResult.liquidityFactor * 10) / 10;
                return (
                  <div key={index} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-center space-y-1">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                      Year {index + 1} ({Math.round(equityResult.vestSplits[index] * 100)}%)
                    </span>
                    <span className="text-base font-extrabold font-mono text-indigo-600 block">
                      ₹ {realizable}L
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      Paper: ₹ {vestAmount}L
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Exercise Trap Alert */}
          {equityResult.exerciseTrapWarning && (
            <div className="bg-rose-50 border border-rose-200 rounded-2xl p-5 space-y-2">
              <div className="flex items-center gap-2 text-rose-800 font-bold text-sm">
                <AlertTriangle className="w-5 h-5 text-rose-600" />
                <span>The 90-Day Golden Handcuffs Trap</span>
              </div>
              <p className="text-xs text-rose-800 leading-relaxed">
                {equityResult.exerciseTrapWarning}
              </p>
              <div className="text-xs font-mono text-rose-900 bg-rose-100 p-2.5 rounded-lg border border-rose-200">
                <strong>Recommended Counter:</strong> Request a 5-year or 7-year extended post-termination exercise window (PTEW) to prevent equity forfeiture upon departure.
              </div>
            </div>
          )}

          {/* Section 17(2) Perquisite Tax Explanation */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Lock className="w-4 h-4 text-slate-700" />
              <span>Section 17(2) Perquisite Tax in India</span>
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Under Indian Income Tax Law, equity vesting is a two-stage taxable event:
            </p>
            <div className="grid grid-cols-2 gap-3 text-xs pt-1">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <strong className="block text-slate-900 mb-1">Stage 1: Vesting / Exercise</strong>
                <p className="text-slate-600 text-[11px]">
                  Taxed as perquisite income under Section 17(2) at your highest marginal income tax slab (~31.2%). For Year 1, this equals approximately <strong>₹ {equityResult.perquisiteTaxYear1Lpa} LPA</strong> in tax.
                </p>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <strong className="block text-slate-900 mb-1">Stage 2: Eventual Sale / Exit</strong>
                <p className="text-slate-600 text-[11px]">
                  Taxed under Capital Gains. Unlisted shares held &gt; 24 months qualify for Long-Term Capital Gains (LTCG) at 12.5% (Budget 2024 revision).
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
