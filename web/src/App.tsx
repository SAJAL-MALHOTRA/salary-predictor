import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { InteractivePaySlip } from './components/InteractivePaySlip';
import { VisualContractRedliner } from './components/VisualContractRedliner';
import { OldVsNewTaxOptimizer } from './components/OldVsNewTaxOptimizer';
import { MultiOfferDecisionMatrix } from './components/MultiOfferDecisionMatrix';
import { EquityValuationModeler } from './components/EquityValuationModeler';
import { RecruiterChatCopilot } from './components/RecruiterChatCopilot';
import type { OfferInput } from './types';
import { calculateTakeHomeNewRegime } from './lib/taxEngine';
import { auditOfferContract } from './lib/contractAuditor';
import { ShieldCheck, Lock, CheckCircle2, Sparkles } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'AUDIT' | 'REDLINE' | 'TAX_OPTIMIZER' | 'COMPARE' | 'EQUITY' | 'COPILOT'>('AUDIT');

  const [offer, setOffer] = useState<OfferInput>({
    company: 'Swiggy',
    role: 'Software Engineer II',
    city: 'Bangalore',
    expYears: 4,
    ctcLpa: 24.0,
    variablePct: 15,
    joiningBonusLpa: 2.0,
    gratuityIncluded: true,
    variableFreq: 'Annual',
    expectedTenureYears: 2.0,
    noticePeriodDays: 60,
  });

  // Fixed portion of CTC determines regular monthly base salary calculation
  const fixedCtcLpa = offer.ctcLpa * (1.0 - offer.variablePct / 100.0);
  const takeHome = calculateTakeHomeNewRegime(fixedCtcLpa);
  const audit = auditOfferContract(
    offer.ctcLpa,
    offer.variablePct,
    offer.gratuityIncluded,
    offer.joiningBonusLpa,
    12,
    offer.noticePeriodDays,
    offer.variableFreq,
    offer.expectedTenureYears
  );

  return (
    <div className="min-h-screen bg-[#F7F8FA] text-[#151922] flex flex-col font-sans">
      {/* Sticky Navigation */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <section className="text-center max-w-3xl mx-auto space-y-3 pt-2 pb-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>India Tech Offer Intelligence</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight leading-tight">
            Your CTC isn&apos;t your salary.
          </h1>

          <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-2xl mx-auto">
            Understand your actual monthly take-home, uncover compensation traps, benchmark your offer, and negotiate with confidence.
          </p>

          {/* Trust Points */}
          <div className="flex flex-wrap items-center justify-center gap-6 pt-2 text-xs text-slate-500 font-medium">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>No signup required</span>
            </div>
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-indigo-600" />
              <span>Transparent calculation breakdown</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Lock className="w-4 h-4 text-slate-600" />
              <span>Your offer details stay private</span>
            </div>
          </div>
        </section>

        {/* Tab Content Rendering */}
        <div className="transition-opacity duration-200">
          {activeTab === 'AUDIT' && (
            <InteractivePaySlip
              offer={offer}
              setOffer={setOffer}
              takeHome={takeHome}
              audit={audit}
              onNavigateToTab={setActiveTab}
            />
          )}

          {activeTab === 'REDLINE' && (
            <VisualContractRedliner
              offer={offer}
              audit={audit}
              onNavigateToCopilot={() => setActiveTab('COPILOT')}
            />
          )}

          {activeTab === 'TAX_OPTIMIZER' && (
            <OldVsNewTaxOptimizer offer={offer} />
          )}

          {activeTab === 'COMPARE' && (
            <MultiOfferDecisionMatrix />
          )}

          {activeTab === 'EQUITY' && (
            <EquityValuationModeler offer={offer} />
          )}

          {activeTab === 'COPILOT' && (
            <RecruiterChatCopilot offer={offer} />
          )}
        </div>
      </main>

      {/* Production-Grade Fintech Footer */}
      <footer className="bg-white border-t border-slate-200 mt-16 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 border-b border-slate-100 pb-6 text-xs text-slate-500">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-indigo-600 flex items-center justify-center text-white font-bold text-xs">
                OI
              </div>
              <span className="font-bold text-slate-800">Offer Intelligence</span>
              <span>— India Tech Compensation Engine</span>
            </div>
            <div className="flex items-center gap-6">
              <span>Budget 2024 Compliant</span>
              <span>Payment of Gratuity Act 1972</span>
              <span>Section 10(13A) HRA</span>
              <span>Section 17(2) Perquisite</span>
            </div>
          </div>

          <p className="text-[11px] text-slate-400 leading-relaxed text-center sm:text-left">
            Disclaimer: Offer Intelligence is an educational and financial modeling tool for technology professionals in India. Calculations are derived strictly from statutory rules including the Income Tax Act 1961 (Budget 2024 revisions), Payment of Gratuity Act 1972, and Employees&apos; Provident Funds and Miscellaneous Provisions Act 1952. This application does not provide formal legal, tax, or financial advice. Consult a certified Chartered Accountant (CA) or employment attorney for binding contractual negotiations.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
