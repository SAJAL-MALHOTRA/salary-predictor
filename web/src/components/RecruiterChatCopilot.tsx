import React, { useState } from 'react';
import type { OfferInput } from '../types';
import { analyzeRecruiterMessage } from '../lib/negotiationCopilot';
import type { CopilotAnalysis } from '../lib/negotiationCopilot';
import { MessageSquare, Sparkles, Copy, Check, ShieldAlert, Send } from 'lucide-react';

interface RecruiterChatCopilotProps {
  offer: OfferInput;
}

export const RecruiterChatCopilot: React.FC<RecruiterChatCopilotProps> = ({ offer }) => {
  const [pastedMessage, setPastedMessage] = useState<string>(
    "Hi! Congratulations on the offer. Please note this offer is valid for 48 hours only, after which we will need to extend it to the next candidate in line. Please sign and return the letter by EOD tomorrow."
  );
  const [targetCtcLpa, setTargetCtcLpa] = useState<number>(offer.ctcLpa * 1.15);
  const [copiedScript, setCopiedScript] = useState<'email' | 'whatsapp' | null>(null);

  const analysis: CopilotAnalysis = analyzeRecruiterMessage(
    pastedMessage,
    offer.role,
    offer.company,
    targetCtcLpa
  );

  const handleCopy = (text: string, type: 'email' | 'whatsapp') => {
    navigator.clipboard.writeText(text);
    setCopiedScript(type);
    setTimeout(() => setCopiedScript(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Recruiter Negotiation War Room</h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              Live Tactical Copilot
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Paste the exact message received from HR or the recruiter. The copilot detects hidden pressure tactics and generates battle-tested Email & WhatsApp counter-responses.
          </p>
        </div>

        {/* Target Counter CTC Input */}
        <div className="flex items-center gap-2 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
          <span className="text-xs font-semibold text-slate-600">Counter Target:</span>
          <div className="relative">
            <span className="absolute left-2.5 top-1.5 text-xs text-slate-400">₹</span>
            <input
              type="number"
              step="0.5"
              value={targetCtcLpa.toFixed(1)}
              onChange={(e) => setTargetCtcLpa(parseFloat(e.target.value) || 0)}
              className="w-24 pl-5 pr-2 py-1 text-xs font-mono font-bold bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <span className="absolute right-2 top-1.5 text-[10px] text-slate-400">LPA</span>
          </div>
        </div>
      </div>

      {/* Preset Recruiter Pressure Tactic Chips */}
      <div className="flex flex-wrap items-center gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs">
        <span className="font-semibold text-slate-600 flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-indigo-600" /> Test Common Tactics:
        </span>
        <button
          onClick={() => setPastedMessage("Hi! Please note this offer is valid for 48 hours only, after which we will need to extend it to the next candidate in line. Please sign and return the letter by tomorrow.")}
          className="px-2.5 py-1 bg-white hover:bg-slate-100 rounded-md border border-slate-200 text-slate-700 font-medium transition-all"
        >
          48h Exploding Deadline
        </button>
        <button
          onClick={() => setPastedMessage("Our company policy strictly caps lateral hikes at 20% on last drawn CTC. We cannot exceed this band regardless of other offers.")}
          className="px-2.5 py-1 bg-white hover:bg-slate-100 rounded-md border border-slate-200 text-slate-700 font-medium transition-all"
        >
          20% Policy Hike Ceiling
        </button>
        <button
          onClick={() => setPastedMessage("We cannot increase the fixed salary due to internal equity, but we have revised the performance bonus to 35% variable to meet your 25 LPA CTC request.")}
          className="px-2.5 py-1 bg-white hover:bg-slate-100 rounded-md border border-slate-200 text-slate-700 font-medium transition-all"
        >
          Shift Base to Variable Pay
        </button>
      </div>

      {/* 2-Column Split: Message Ingestion (Left) & Tactical Analysis + Responses (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Message Input Area */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center border-b border-slate-100 pb-3">
            <label className="text-xs font-bold text-slate-800 uppercase tracking-wide">
              Pasted Recruiter Message (WhatsApp / Email)
            </label>
            <span className="text-[11px] text-slate-400 font-mono">{pastedMessage.length} chars</span>
          </div>

          <textarea
            rows={7}
            value={pastedMessage}
            onChange={(e) => setPastedMessage(e.target.value)}
            placeholder="Paste recruiter's message here..."
            className="w-full p-3.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans leading-relaxed text-slate-800"
          />

          {/* Tactical Diagnostic Card */}
          <div className="bg-slate-900 text-white p-5 rounded-xl space-y-3.5">
            <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase tracking-wide">
              <ShieldAlert className="w-4 h-4 text-rose-500" />
              <span>Detected: {analysis.detectedTactic}</span>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Recruiter Constraint:</span>
              <p className="text-xs text-slate-300 leading-relaxed">
                {analysis.recruiterConstraint}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Your True Leverage:</span>
              <p className="text-xs text-emerald-300 leading-relaxed">
                {analysis.candidateAdvantage}
              </p>
            </div>

            <div className="space-y-1 pt-1 border-t border-slate-800">
              <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider block">Recommended Strategy:</span>
              <p className="text-xs text-slate-200 leading-relaxed font-medium">
                {analysis.recommendedMove}
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Tailored Counter Scripts */}
        <div className="lg:col-span-7 space-y-6">
          {/* Email Script Card */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
              <div className="flex items-center gap-2">
                <Send className="w-4 h-4 text-indigo-600" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">Official Email Response</h3>
              </div>
              <button
                onClick={() => handleCopy(analysis.emailResponse, 'email')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all"
              >
                {copiedScript === 'email' ? <Check className="w-3.5 h-3.5 text-emerald-300" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedScript === 'email' ? 'Copied to Clipboard' : 'Copy Email'}</span>
              </button>
            </div>

            <div className="p-6">
              <pre className="text-xs text-slate-700 font-sans whitespace-pre-wrap leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100 font-mono">
                {analysis.emailResponse}
              </pre>
            </div>
          </div>

          {/* WhatsApp / Quick DM Script Card */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-emerald-50/40">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-emerald-600" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-950">WhatsApp / Direct Message Script</h3>
              </div>
              <button
                onClick={() => handleCopy(analysis.whatsAppResponse, 'whatsapp')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all"
              >
                {copiedScript === 'whatsapp' ? <Check className="w-3.5 h-3.5 text-white" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedScript === 'whatsapp' ? 'Copied to Clipboard' : 'Copy WhatsApp'}</span>
              </button>
            </div>

            <div className="p-6">
              <p className="text-xs text-slate-800 leading-relaxed bg-emerald-50/30 p-4 rounded-xl border border-emerald-100 font-sans">
                &ldquo;{analysis.whatsAppResponse}&rdquo;
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
