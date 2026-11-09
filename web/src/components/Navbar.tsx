import React from 'react';
import { ShieldCheck, FileText, Scale, TrendingUp, MessageSquare } from 'lucide-react';

interface NavbarProps {
  activeTab: 'AUDIT' | 'REDLINE' | 'TAX_OPTIMIZER' | 'COMPARE' | 'EQUITY' | 'COPILOT';
  setActiveTab: (tab: 'AUDIT' | 'REDLINE' | 'TAX_OPTIMIZER' | 'COMPARE' | 'EQUITY' | 'COPILOT') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-sm shadow-indigo-200">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 tracking-tight text-lg">Offer Intelligence</span>
                <span className="text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Budget 2024
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">India Tech Compensation & Contract Risk Engine</p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={() => setActiveTab('AUDIT')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'AUDIT'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Offer Audit</span>
            </button>

            <button
              onClick={() => setActiveTab('REDLINE')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'REDLINE'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Visual Redliner</span>
            </button>

            <button
              onClick={() => setActiveTab('TAX_OPTIMIZER')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'TAX_OPTIMIZER'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span>Tax Optimizer</span>
            </button>

            <button
              onClick={() => setActiveTab('COMPARE')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'COMPARE'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Compare</span>
            </button>

            <button
              onClick={() => setActiveTab('EQUITY')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'EQUITY'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Equity / ESOP</span>
            </button>

            <button
              onClick={() => setActiveTab('COPILOT')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'COPILOT'
                  ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-200'
                  : 'text-indigo-600 hover:bg-indigo-50'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>War Room</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
