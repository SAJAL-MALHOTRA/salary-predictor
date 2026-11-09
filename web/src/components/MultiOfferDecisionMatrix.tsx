import React, { useState } from 'react';
import type { OfferProfile } from '../types';
import { calculateTakeHomeNewRegime } from '../lib/taxEngine';
import { Scale, Plus, Trash2 } from 'lucide-react';

export const MultiOfferDecisionMatrix: React.FC = () => {
  const [offers, setOffers] = useState<OfferProfile[]>([
    {
      id: 'current',
      name: 'Current Job',
      company: 'TCS / Wipro',
      role: 'Senior Systems Engineer',
      ctcLpa: 11.5,
      variablePct: 10,
      joiningBonusLpa: 0,
      noticePeriodDays: 90,
      monthlyInHand: 72400,
      guaranteedCashLpa: 10.35,
      tierNum: 1,
      riskScore: 28,
    },
    {
      id: 'offer-a',
      name: 'Offer A (High Base)',
      company: 'Razorpay / Swiggy',
      role: 'Software Engineer II',
      ctcLpa: 24.0,
      variablePct: 10,
      joiningBonusLpa: 2.0,
      noticePeriodDays: 60,
      monthlyInHand: 142300,
      guaranteedCashLpa: 21.6,
      tierNum: 2,
      riskScore: 18,
    },
    {
      id: 'offer-b',
      name: 'Offer B (High Variable)',
      company: 'Early-Stage FinTech',
      role: 'Founding Engineer',
      ctcLpa: 28.0,
      variablePct: 30,
      joiningBonusLpa: 3.0,
      noticePeriodDays: 30,
      monthlyInHand: 131800,
      guaranteedCashLpa: 19.6,
      tierNum: 3,
      riskScore: 45,
    },
  ]);

  const [newCompanyName, setNewCompanyName] = useState('');
  const [newCtc, setNewCtc] = useState<number>(20);
  const [newVarPct, setNewVarPct] = useState<number>(15);

  const handleAddOffer = () => {
    if (!newCompanyName.trim()) return;
    const takeHome = calculateTakeHomeNewRegime(newCtc * (1 - newVarPct / 100));
    const newOffer: OfferProfile = {
      id: `offer-${Date.now()}`,
      name: `Offer ${offers.length}`,
      company: newCompanyName,
      role: 'Software Engineer',
      ctcLpa: newCtc,
      variablePct: newVarPct,
      joiningBonusLpa: 1.0,
      noticePeriodDays: 60,
      monthlyInHand: takeHome.monthlyInHand,
      guaranteedCashLpa: Math.round(newCtc * (1 - newVarPct / 100) * 100) / 100,
      tierNum: offers.length + 1,
      riskScore: newVarPct > 20 ? 40 : 20,
    };
    setOffers([...offers, newOffer]);
    setNewCompanyName('');
  };

  const handleRemoveOffer = (id: string) => {
    setOffers(offers.filter(o => o.id !== id));
  };

  const currentJob = offers.find(o => o.id === 'current') || offers[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Multi-Offer Decision Matrix</h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
              Side-by-Side Analysis
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Compare monthly cash flow deltas, notice period buyout recovery breakeven, and contractual risk scores.
          </p>
        </div>

        {/* Quick Add Form */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Company Name"
            value={newCompanyName}
            onChange={(e) => setNewCompanyName(e.target.value)}
            className="px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            type="number"
            placeholder="CTC (LPA)"
            value={newCtc || ''}
            onChange={(e) => setNewCtc(parseFloat(e.target.value) || 0)}
            className="w-20 px-2 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none font-mono"
          />
          <input
            type="number"
            placeholder="Var %"
            value={newVarPct || ''}
            onChange={(e) => setNewVarPct(parseInt(e.target.value) || 0)}
            className="w-16 px-2 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none font-mono"
          />
          <button
            onClick={handleAddOffer}
            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add</span>
          </button>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {offers.map((offer) => {
          const isCurrent = offer.id === 'current';
          const monthlyDelta = offer.monthlyInHand - currentJob.monthlyInHand;
          // Buyout Breakeven: Notice period difference * 1 month current salary / monthly delta
          const buyoutMonths = monthlyDelta > 0 ? Math.max(0.5, Math.round(((offer.noticePeriodDays / 30) * (currentJob.monthlyInHand / monthlyDelta)) * 10) / 10) : 0;

          return (
            <div
              key={offer.id}
              className={`bg-white rounded-2xl border p-6 space-y-5 transition-all relative ${
                isCurrent
                  ? 'border-slate-200 shadow-sm'
                  : offer.guaranteedCashLpa >= 20
                  ? 'border-indigo-400 ring-2 ring-indigo-100 shadow-md'
                  : 'border-slate-200 shadow-sm'
              }`}
            >
              {/* Header */}
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">{offer.name}</span>
                  <h3 className="text-base font-extrabold text-slate-900 mt-0.5">{offer.company}</h3>
                  <p className="text-xs text-slate-500">{offer.role}</p>
                </div>
                {!isCurrent && (
                  <button
                    onClick={() => handleRemoveOffer(offer.id)}
                    className="text-slate-400 hover:text-rose-600 transition-colors p-1"
                    title="Remove offer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Monthly In-Hand */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block">Monthly In-Hand Cash</span>
                <div className="text-2xl font-black font-mono text-slate-900 mt-1">
                  ₹ {offer.monthlyInHand.toLocaleString('en-IN')}
                </div>
                {!isCurrent && (
                  <div className={`text-xs font-bold mt-1.5 flex items-center gap-1 ${
                    monthlyDelta >= 0 ? 'text-emerald-600' : 'text-rose-600'
                  }`}>
                    <span>{monthlyDelta >= 0 ? `+₹ ${monthlyDelta.toLocaleString('en-IN')} / mo vs current` : `-₹ ${Math.abs(monthlyDelta).toLocaleString('en-IN')} / mo`}</span>
                  </div>
                )}
              </div>

              {/* Key Offer Metrics */}
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Headline CTC</span>
                  <span className="font-mono font-bold text-slate-800">₹ {offer.ctcLpa.toFixed(1)} LPA</span>
                </div>

                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Guaranteed Year 1 Cash</span>
                  <span className="font-mono font-bold text-indigo-600">₹ {offer.guaranteedCashLpa.toFixed(1)} LPA</span>
                </div>

                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Variable %</span>
                  <span className="font-mono font-medium text-amber-600">{offer.variablePct}%</span>
                </div>

                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Notice Period</span>
                  <span className="font-mono font-medium text-slate-700">{offer.noticePeriodDays} Days</span>
                </div>

                {!isCurrent && (
                  <div className="flex justify-between py-1 border-b border-slate-100 bg-emerald-50/50 px-2 rounded">
                    <span className="text-emerald-900 font-semibold">Notice Buyout Breakeven</span>
                    <span className="font-mono font-bold text-emerald-800">{buyoutMonths} months</span>
                  </div>
                )}

                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Contractual Risk Score</span>
                  <span className={`font-mono font-bold ${
                    offer.riskScore > 35 ? 'text-rose-600' : offer.riskScore > 20 ? 'text-amber-600' : 'text-emerald-600'
                  }`}>
                    {offer.riskScore}/100 ({offer.riskScore > 35 ? 'High Risk' : offer.riskScore > 20 ? 'Moderate' : 'Low Risk'})
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
