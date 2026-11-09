import React, { useState } from 'react';
import type { OfferInput, ContractAuditResult } from '../types';
import { ShieldAlert, AlertTriangle, CheckCircle, Copy, Check, FileSignature, MessageSquare, ArrowRight, CornerDownRight } from 'lucide-react';

interface VisualContractRedlinerProps {
  offer: OfferInput;
  audit: ContractAuditResult;
  onNavigateToCopilot: () => void;
}

export const VisualContractRedliner: React.FC<VisualContractRedlinerProps> = ({
  offer,
  audit,
  onNavigateToCopilot
}) => {
  const [selectedRiskId, setSelectedRiskId] = useState<string>(
    audit.risks.length > 0 ? audit.risks[0].id : ''
  );
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const selectedRisk = audit.risks.find((r) => r.id === selectedRiskId) || audit.risks[0];

  const handleCopyClause = (clause: string, id: string) => {
    navigator.clipboard.writeText(clause);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getSeverityBadge = (severity: 'HIGH' | 'MEDIUM' | 'CLEAN') => {
    switch (severity) {
      case 'HIGH':
        return (
          <span className="px-2 py-0.5 text-[11px] font-bold rounded-full bg-rose-100 text-rose-800 border border-rose-200 flex items-center gap-1">
            <ShieldAlert className="w-3 h-3 text-rose-600" /> HIGH RISK
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="px-2 py-0.5 text-[11px] font-bold rounded-full bg-amber-100 text-amber-800 border border-amber-200 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3 text-amber-600" /> CAUTION
          </span>
        );
      case 'CLEAN':
        return (
          <span className="px-2 py-0.5 text-[11px] font-bold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-emerald-600" /> FAVORABLE
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Redliner Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileSignature className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Visual Contract Redliner</h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
              {audit.risks.filter(r => r.severity === 'HIGH').length} High-Risk Clauses Found
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Click any highlighted clause in the simulated offer letter to examine statutory legal traps, financial impact in ₹, and pre-drafted counter-amendments.
          </p>
        </div>

        <button
          onClick={onNavigateToCopilot}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-sm shadow-indigo-200 transition-all self-start md:self-auto"
        >
          <MessageSquare className="w-4 h-4" />
          <span>Negotiate with Recruiter</span>
        </button>
      </div>

      {/* 2-Column Split: Document Viewer (Left) & Risk Inspector Drawer (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Simulated Paper Document */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-300 shadow-lg p-8 sm:p-10 font-serif relative overflow-hidden">
          {/* Paper Letterhead */}
          <div className="border-b-2 border-slate-900 pb-5 mb-6 font-sans">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-extrabold text-xl text-slate-900 tracking-tight uppercase">
                  {offer.company} TECHNOLOGY INDIA PRIVATE LIMITED
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">Corporate Identity No: U72200KA2018PTC112345 · Registered Office: Outer Ring Road, Bangalore</p>
              </div>
              <span className="text-[10px] font-mono uppercase bg-slate-100 text-slate-600 px-2 py-1 rounded border border-slate-200">
                Annexure A
              </span>
            </div>
            <div className="mt-4 text-xs font-mono text-slate-600 flex justify-between">
              <span>Candidate: [Candidate Name]</span>
              <span>Designation: {offer.role}</span>
              <span>CTC: ₹ {offer.ctcLpa} LPA</span>
            </div>
          </div>

          {/* Letter Body Clauses */}
          <div className="space-y-6 text-sm text-slate-800 leading-relaxed">
            <p className="font-sans text-xs uppercase tracking-wider text-slate-400 font-bold">
              TERMS AND CONDITIONS OF EMPLOYMENT
            </p>

            {/* Clause 1: Appointment */}
            <div className="space-y-1">
              <h4 className="font-sans font-bold text-xs text-slate-900">1. Appointment & Base Compensation</h4>
              <p className="text-xs text-slate-600">
                You will be appointed to the position of <strong>{offer.role}</strong> with a total Cost to Company (CTC) of <strong>₹ {offer.ctcLpa} Lakhs per annum</strong>. Basic salary is allocated at 40% of CTC.
              </p>
            </div>

            {/* Clause 4.1: Gratuity Lock */}
            <div
              onClick={() => setSelectedRiskId(audit.risks.find(r => r.id.startsWith('gratuity'))?.id || '')}
              className={`p-3.5 rounded-xl transition-all cursor-pointer border ${
                selectedRisk?.id.startsWith('gratuity')
                  ? 'bg-rose-50/80 border-rose-400 ring-2 ring-rose-300'
                  : 'bg-rose-50/30 border-rose-200 hover:bg-rose-50/60'
              }`}
            >
              <div className="flex items-center justify-between font-sans mb-1.5">
                <span className="text-xs font-bold text-rose-900">Clause 4.1 — Gratuity Treatment</span>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-200 text-rose-900">
                  {offer.expectedTenureYears < 5 ? '[RED] 5-YEAR LOCK' : '[CLEAN] VESTED'}
                </span>
              </div>
              <p className="text-xs text-slate-800 italic">
                &ldquo;Gratuity will be payable strictly in accordance with the provisions of the Payment of Gratuity Act, 1972, deducted from annual CTC at 4.81% of basic salary.&rdquo;
              </p>
              <div className="mt-2 flex items-center gap-1.5 font-sans text-[11px] font-semibold text-rose-800">
                <CornerDownRight className="w-3.5 h-3.5" />
                <span>Financial Impact: ₹ {audit.annualGratuityRupees.toLocaleString('en-IN')}/yr loss if tenure &lt; 5 years</span>
              </div>
            </div>

            {/* Clause 5.2: Variable Compensation */}
            {offer.variablePct > 0 && (
              <div
                onClick={() => setSelectedRiskId(audit.risks.find(r => r.id.startsWith('variable'))?.id || '')}
                className={`p-3.5 rounded-xl transition-all cursor-pointer border ${
                  selectedRisk?.id.startsWith('variable')
                    ? 'bg-amber-50/80 border-amber-400 ring-2 ring-amber-300'
                    : 'bg-amber-50/30 border-amber-200 hover:bg-amber-50/60'
                }`}
              >
                <div className="flex items-center justify-between font-sans mb-1.5">
                  <span className="text-xs font-bold text-amber-900">Clause 5.2 — Annual Performance Pay</span>
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-200 text-amber-900">
                    [AMBER] {offer.variableFreq.toUpperCase()} CYCLE
                  </span>
                </div>
                <p className="text-xs text-slate-800 italic">
                  &ldquo;The employee is eligible for variable pay up to {offer.variablePct}% of CTC (₹ {audit.variableLpa} LPA). Payout is contingent upon company EBITDA and individual ratings. The employee must be actively employed and not serving notice on disbursement date.&rdquo;
                </p>
                <div className="mt-2 flex items-center gap-1.5 font-sans text-[11px] font-semibold text-amber-800">
                  <CornerDownRight className="w-3.5 h-3.5" />
                  <span>Exit Forfeiture Exposure: ₹ {Math.round(audit.variableLpa * 100000).toLocaleString('en-IN')}</span>
                </div>
              </div>
            )}

            {/* Clause 6.3: Joining Bonus Clawback */}
            {offer.joiningBonusLpa > 0 && (
              <div
                onClick={() => setSelectedRiskId('clawback-tax-trap')}
                className={`p-3.5 rounded-xl transition-all cursor-pointer border ${
                  selectedRisk?.id === 'clawback-tax-trap'
                    ? 'bg-rose-50/80 border-rose-400 ring-2 ring-rose-300'
                    : 'bg-rose-50/30 border-rose-200 hover:bg-rose-50/60'
                }`}
              >
                <div className="flex items-center justify-between font-sans mb-1.5">
                  <span className="text-xs font-bold text-rose-900">Clause 6.3 — Joining Bonus Recovery</span>
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-200 text-rose-900">
                    [RED] SEC 89(1) CLAWBACK
                  </span>
                </div>
                <p className="text-xs text-slate-800 italic">
                  &ldquo;In consideration of joining, the company shall disburse a one-time sign-on bonus of ₹ {offer.joiningBonusLpa} LPA. In the event of separation within 12 months, the employee shall repay 100% of the gross bonus.&rdquo;
                </p>
                <div className="mt-2 flex items-center gap-1.5 font-sans text-[11px] font-semibold text-rose-800">
                  <CornerDownRight className="w-3.5 h-3.5" />
                  <span>Out-of-Pocket Tax Deficit: ₹ {Math.round(offer.joiningBonusLpa * 100000 * 0.312).toLocaleString('en-IN')} required in cash</span>
                </div>
              </div>
            )}

            {/* Clause 8.1: Notice Period */}
            <div
              onClick={() => setSelectedRiskId(audit.risks.find(r => r.id.startsWith('notice'))?.id || '')}
              className={`p-3.5 rounded-xl transition-all cursor-pointer border ${
                selectedRisk?.id.startsWith('notice')
                  ? offer.noticePeriodDays >= 90
                    ? 'bg-rose-50/80 border-rose-400 ring-2 ring-rose-300'
                    : 'bg-amber-50/80 border-amber-400 ring-2 ring-amber-300'
                  : 'bg-slate-50 border-slate-200 hover:bg-slate-100/60'
              }`}
            >
              <div className="flex items-center justify-between font-sans mb-1.5">
                <span className="text-xs font-bold text-slate-900">Clause 8.1 — Termination & Notice Period</span>
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                  offer.noticePeriodDays >= 90 ? 'bg-rose-200 text-rose-900' : 'bg-amber-200 text-amber-900'
                }`}>
                  {offer.noticePeriodDays} DAYS
                </span>
              </div>
              <p className="text-xs text-slate-800 italic">
                &ldquo;Either party may terminate this agreement by giving {offer.noticePeriodDays} days notice in writing. Buyout of notice period is solely at the management&apos;s discretion.&rdquo;
              </p>
              <div className="mt-2 flex items-center gap-1.5 font-sans text-[11px] font-semibold text-slate-700">
                <CornerDownRight className="w-3.5 h-3.5" />
                <span>Lateral mobility risk: Recruiter offers rescinded due to &gt;45 day joining delay</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Risk Deep Dive & Counter-Amendment Drawer */}
        <div className="lg:col-span-5 space-y-6">
          {selectedRisk ? (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6 sticky top-24">
              {/* Header */}
              <div className="space-y-2 border-b border-slate-100 pb-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">{selectedRisk.clauseRef}</span>
                  {getSeverityBadge(selectedRisk.severity)}
                </div>
                <h3 className="text-base font-bold text-slate-900">{selectedRisk.title}</h3>
                <span className="text-xs font-semibold text-indigo-600 block">{selectedRisk.category}</span>
              </div>

              {/* Financial Impact in Rupees */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block">Calculated Financial Impact</span>
                <div className="text-sm font-bold text-slate-900 mt-1 font-mono">
                  {selectedRisk.financialImpact}
                </div>
              </div>

              {/* Why It Matters */}
              <div className="space-y-1.5">
                <span className="text-xs font-bold text-slate-900">Why this matters:</span>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {selectedRisk.whyItMatters}
                </p>
              </div>

              {/* Action */}
              <div className="space-y-1.5">
                <span className="text-xs font-bold text-slate-900">What you should verify:</span>
                <p className="text-xs text-slate-600 leading-relaxed bg-amber-50/50 p-3 rounded-lg border border-amber-200/60">
                  {selectedRisk.verificationAction}
                </p>
              </div>

              {/* Redline Amendment */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">Recommended Counter-Amendment:</span>
                  <button
                    onClick={() => handleCopyClause(selectedRisk.counterAmendment, selectedRisk.id)}
                    className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-600 hover:text-indigo-800"
                  >
                    {copiedId === selectedRisk.id ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedId === selectedRisk.id ? 'Copied' : 'Copy Clause'}</span>
                  </button>
                </div>
                <div className="p-3.5 bg-slate-900 text-slate-100 rounded-xl text-xs font-mono leading-relaxed border border-slate-800">
                  {selectedRisk.counterAmendment}
                </div>
              </div>

              {/* CTA to War Room */}
              <button
                onClick={onNavigateToCopilot}
                className="w-full py-2.5 px-4 bg-slate-100 hover:bg-slate-200 text-slate-900 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 border border-slate-300"
              >
                <span>Draft Recruiter Counter-Offer with this Clause</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center text-slate-500 py-12">
              Select any highlighted clause in the document viewer to inspect risk details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
