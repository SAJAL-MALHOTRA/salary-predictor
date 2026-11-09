export interface CopilotAnalysis {
  detectedTactic: string;
  recruiterConstraint: string;
  candidateAdvantage: string;
  recommendedMove: string;
  emailResponse: string;
  whatsAppResponse: string;
}

export function analyzeRecruiterMessage(
  message: string,
  candidateRole: string = 'Software Engineer',
  companyName: string = 'Target Company',
  targetCtcLpa: number = 22.0
): CopilotAnalysis {
  const text = message.toLowerCase();

  if (text.includes('48 hour') || text.includes('today') || text.includes('eod') || text.includes('expire') || text.includes('deadline')) {
    return {
      detectedTactic: 'Exploding Offer / Artificial Deadline Urgency',
      recruiterConstraint: 'Recruiter wants to close their monthly hiring quota and prevent you from completing competing interviews or soliciting counter-offers.',
      candidateAdvantage: 'They already invested 4+ interview rounds into you. Reopening the candidate search costs them ₹2–3 Lakhs and 6 weeks of engineering team time.',
      recommendedMove: 'Defuse the deadline with genuine enthusiasm while establishing a firm, reasonable 4-5 business day decision window to review terms.',
      emailResponse: `Subject: Regarding decision timeline for ${candidateRole} - ${companyName}\n\nDear Hiring Team,\n\nThank you for extending the formal offer. I am genuinely enthusiastic about the opportunity to join ${companyName} and contribute to the team's roadmap.\n\nEvaluating a career transition is an important decision for my family and me. To properly review the contractual annexures, statutory clauses, and benefits documentation, I would appreciate until Friday to provide my final confirmed response.\n\nI want to make sure I enter this role with 100% clarity and commitment. Thank you for your understanding, and I will be back in touch before Friday.\n\nBest regards,\n[Your Name]`,
      whatsAppResponse: `Hi! Thank you so much for the offer. I'm really excited about ${companyName} and the role. Evaluating this transition is a significant decision, so I'd appreciate until Friday to thoroughly review the offer letter terms with my family. I want to give you my 100% committed confirmation then!`,
    };
  }

  if (text.includes('20%') || text.includes('policy') || text.includes('standard hike') || text.includes('cap')) {
    return {
      detectedTactic: 'HR Policy Ceiling / Lateral Hike Cap',
      recruiterConstraint: 'Recruiter is bound by compensation council guidelines that anchor hikes to your prior salary rather than role market value.',
      candidateAdvantage: 'Your prior compensation reflects outdated responsibilities at an old firm. The new role has higher scope and domain market value.',
      recommendedMove: 'Respect the base salary ceiling, but negotiate a Year-1 joining bonus or retention grant to bridge the rupee gap without violating HR band policy.',
      emailResponse: `Subject: Regarding compensation structure for ${candidateRole} - ${companyName}\n\nDear Hiring Team,\n\nThank you for sharing the proposed package. I understand internal guidelines often baseline against prior compensation.\n\nHowever, my current compensation reflects a legacy baseline before my responsibilities expanded into critical architecture and delivery. Based on current lateral benchmarks for ${candidateRole}, market parity sits closer to ₹ ${targetCtcLpa.toFixed(1)} LPA.\n\nIf the base salary band has a firm ceiling, I am open to structuring the delta as a Year-1 joining bonus or enhanced upfront equity grant. This allows us to maintain internal band parity while bridging the compensation gap.\n\nBest regards,\n[Your Name]`,
      whatsAppResponse: `Hi! I understand you have internal percentage guidelines to follow. If the base salary is strictly capped by policy, could we bridge the gap with a one-time joining bonus or Year-1 retention grant? That way your base bands remain untouched while meeting the market benchmark for this role.`,
    };
  }

  if (text.includes('variable') || text.includes('performance') || text.includes('bonus')) {
    return {
      detectedTactic: 'Fixed-to-Variable Risk Shift',
      recruiterConstraint: 'Recruiter is inflating headline CTC while keeping company fixed payroll liabilities low in case quarterly billability dips.',
      candidateAdvantage: 'Contingent variable pay cannot cover mortgage or rent commitments. Banks only evaluate guaranteed cash flow.',
      recommendedMove: 'Request quarterly disbursement rather than annual payout, and ask for written objective performance metrics rather than company-wide revenue gates.',
      emailResponse: `Subject: Regarding variable compensation terms for ${candidateRole} - ${companyName}\n\nDear Hiring Team,\n\nThank you for exploring options on the total package. Regarding the proposed increase in variable pay: to ensure predictable monthly cash flow, I would like to confirm the disbursement mechanics.\n\nIf the additional compensation is allocated to variable pay, I would request that:\n1. Payout frequency be structured quarterly to mitigate exit forfeiture risk, and\n2. Payout gates be tied strictly to objective individual deliverables rather than company-wide margins.\n\nAlternatively, converting a portion into a guaranteed sign-on bonus would make my acceptance immediate.\n\nBest regards,\n[Your Name]`,
      whatsAppResponse: `Thanks for exploring options on the package! Since variable pay is contingent cash flow, could we either disburse it quarterly with clear milestone metrics, or convert part of it into a guaranteed sign-on bonus? That would help me make an immediate decision.`,
    };
  }

  // Default: General Counter / Budget Ceiling
  return {
    detectedTactic: 'Budget Ceiling / Band Anchor',
    recruiterConstraint: 'Recruiter wants to close you at the lower quartile of the approved hiring bracket to maintain recruiting margin.',
    candidateAdvantage: 'You are the hiring manager’s chosen candidate. Recruiters have discretionary authority for sign-on bonuses and non-base perks.',
    recommendedMove: 'Anchor around the 75th percentile of role peers citing domain benchmarks, and offer immediate signature upon alignment.',
    emailResponse: `Subject: Regarding the offer terms for ${candidateRole} - ${companyName}\n\nDear Hiring Team,\n\nThank you very much for extending the offer. I am enthusiastic about the team's technical roadmap and the opportunity to contribute.\n\nI reviewed the proposed package. Based on current lateral hiring benchmarks for ${candidateRole}, I would like to explore if we can align the total compensation closer to ₹ ${targetCtcLpa.toFixed(1)} LPA.\n\nReaching this benchmark reflects market alignment for this scope, and would make my acceptance an immediate decision. I look forward to your thoughts.\n\nBest regards,\n[Your Name]`,
    whatsAppResponse: `Hi! Thank you for the offer—I'm very excited about joining ${companyName}. Based on lateral market benchmarks for this role, could we look at aligning total compensation closer to ₹ ${targetCtcLpa.toFixed(1)} LPA? Reaching this number would allow me to sign immediately!`,
  };
}
