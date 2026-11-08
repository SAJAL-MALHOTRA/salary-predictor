"""
negotiation_war_room.py -- Recruiter Objection Rebuttal & Tactical Counter-Script Engine.

Provides battle-tested rebuttal scripts and psychological frameworks for
the 5 most common Indian recruiter compensation objections:
  1. "Company policy caps lateral hikes at 20%."
  2. "We cannot increase base, but we can increase variable pay."
  3. "We need you in 30 days, but your notice period is 90 days."
  4. "This is our final offer and it expires in 48 hours (Exploding Offer)."
  5. "Internal peer parity doesn't allow higher compensation for this band."
"""

from typing import Dict, Any, List


OBJECTION_PLAYBOOKS: List[Dict[str, Any]] = [
    {
        "id": "hike_cap",
        "title": '1. "Our company policy caps lateral hikes at 20% over your current CTC."',
        "recruiter_motive": "HR compensation councils use percentage caps to prevent compensation inflation and enforce cost control, regardless of market rates.",
        "winning_leverage": "Decouple current compensation from market value. Previous compensation reflects old duties at an old firm; this offer reflects market lateral value for the new role.",
        "email_script": (
            "Subject: Regarding compensation alignment for [Role] - [Company]\n\n"
            "Dear [Recruiter Name],\n\n"
            "Thank you for sharing the proposed package. I understand internal guidelines often baseline against prior compensation. "
            "However, my current compensation reflects a legacy baseline established [X] years ago before my responsibilities expanded into [Key Domain / Tech Stack].\n\n"
            "Based on verified peer benchmarks for [Role Family] at this seniority tier, market median sits at ₹ [Target CTC] LPA. "
            "If your internal base pay band has a firm ceiling, I am open to structuring the delta as a Year-1 joining bonus (₹ [Target Bonus] LPA) "
            "or an enhanced upfront equity grant. This allows us to maintain internal band parity while bridging the compensation gap.\n\n"
            "I am excited to join the team and look forward to reaching an agreement.\n\n"
            "Best regards,\n[Your Name]"
        ),
        "verbal_script": (
            '"I completely understand you have percentage guidelines to follow. However, evaluating this role strictly based on my prior salary '
            'creates a disconnect with the market value of the work I will be executing here. If the fixed base is capped by policy, let\'s solve '
            'it creatively: can we bridge the gap using a one-time joining bonus or Year-1 retention grant so your base bands remain clean?"'
        ),
    },
    {
        "id": "variable_shift",
        "title": '2. "We cannot increase the base salary, but we can increase variable pay."',
        "recruiter_motive": "Inflates quoted CTC on paper while shifting financial downside to the candidate if company margin or appraisal targets drop.",
        "winning_leverage": "Accept performance pay only with contractual evaluation gates, or negotiate non-cash / allowance substitutions that guarantee monthly cash flow.",
        "email_script": (
            "Subject: Regarding variable compensation structure for [Role] - [Company]\n\n"
            "Dear [Recruiter Name],\n\n"
            "Thank you for exploring options on the total package. Regarding the proposed increase in variable pay: to ensure predictable monthly cash flow, "
            "I would like to understand the specific disbursement mechanics.\n\n"
            "If the additional compensation is allocated to variable pay, I would request that:\n"
            "1. Payout frequency be set to quarterly rather than annual to mitigate exit forfeiture risk, and\n"
            "2. The payout criteria be tied strictly to objective individual deliverables rather than company-wide billability gates.\n\n"
            "Alternatively, converting a portion into a guaranteed joining bonus or monthly flexible allowance would make this an immediate decision for me.\n\n"
            "Best regards,\n[Your Name]"
        ),
        "verbal_script": (
            '"I appreciate you finding room in the total package. However, variable pay is contingent cash flow that banks and rent commitments '
            'don\'t recognize. If we cannot move base salary directly, can we convert that delta into a one-time joining bonus or flexible '
            'allowance? If it must stay variable, I\'d need it disbursed quarterly with clear, written performance milestones."'
        ),
    },
    {
        "id": "notice_friction",
        "title": '3. "We need you to join in 30 days, but your current notice period is 90 days."',
        "recruiter_motive": "Hiring manager has urgent project deliverables or an active client billing slot that cannot wait 3 months.",
        "winning_leverage": "Turn notice buyout from a problem into a joint solution: request a buyout reimbursement clause in the offer letter.",
        "email_script": (
            "Subject: Notice period alignment & buyout for [Role] - [Company]\n\n"
            "Dear [Recruiter Name],\n\n"
            "I share the team's urgency to begin onboarding within 30–45 days. My current contractual notice period is 90 days, but I am confident "
            "I can negotiate an early release with my manager by initiating knowledge transfer immediately.\n\n"
            "In the event my current employer demands a notice period buyout for the unserved [30/45] days (estimated at ₹ [Buyout Amount]), "
            "I would like to confirm if [Company] will cover this buyout cost as an upfront expense or addition to the joining bonus. "
            "With this reimbursement confirmed in the offer letter, I will submit my resignation today and commit to the accelerated timeline.\n\n"
            "Best regards,\n[Your Name]"
        ),
        "verbal_script": (
            '"I want to join your team as quickly as possible. I am willing to push my current employer hard for an early release in 30 to 45 days. '
            'However, if they demand a notice buyout for the balance days, will [Company] cover that financial shortfall? If you can include buyout '
            'protection in the offer letter, I can tender my resignation today."'
        ),
    },
    {
        "id": "exploding_offer",
        "title": '4. "This is our final offer and it expires in 48 hours."',
        "recruiter_motive": "Artificial pressure designed to prevent candidates from completing competing interviews or soliciting counter-offers.",
        "winning_leverage": "Defuse the deadline calmly without showing panic. Reaffirm excitement while setting a professional decision boundary.",
        "email_script": (
            "Subject: Regarding the decision timeline for [Role] - [Company]\n\n"
            "Dear [Recruiter Name],\n\n"
            "Thank you for extending the formal offer. I am genuinely enthusiastic about the opportunity to join [Company] and work with [Hiring Manager / Team].\n\n"
            "Evaluating a career transition is an important decision for my family and me. To properly review the contractual annexures, statutory clauses, "
            "and benefits documentation, I would appreciate until [Date - 4-5 business days out] to provide my final confirmed response.\n\n"
            "I want to make sure I enter this role with 100% clarity and commitment. Thank you for your understanding, and I will be back in touch before [Date].\n\n"
            "Best regards,\n[Your Name]"
        ),
        "verbal_script": (
            '"I am very enthusiastic about this offer and [Company] is my top choice. However, 48 hours is too compressed for a major career move '
            'and to review the legal contract terms thoroughly. Can we agree on [Day, e.g. Friday]? That gives me the time needed to review '
            'everything with my family, and I will give you a definitive decision then."'
        ),
    },
    {
        "id": "peer_parity",
        "title": '5. "Internal peer parity doesn\'t allow higher compensation for this band."',
        "recruiter_motive": "Recruiter is protecting internal equity bands and preventing salary inversion with current team members.",
        "winning_leverage": "Respect the base band limit, but negotiate on components that sit outside peer parity (joining bonus, RSUs/ESOPs, accelerated review).",
        "email_script": (
            "Subject: Structuring terms for [Role] - [Company]\n\n"
            "Dear [Recruiter Name],\n\n"
            "I fully respect the importance of internal equity and maintaining balanced compensation bands across the engineering team.\n\n"
            "To respect your base salary bands while achieving competitive market parity, could we structure the package using:\n"
            "1. A one-time sign-on bonus of ₹ [Amount] LPA to bridge Year 1, or\n"
            "2. Additional upfront equity (RSUs/ESOPs) that rewards long-term performance without disrupting internal cash bands, or\n"
            "3. A documented 6-month performance and compensation review checkpoint.\n\n"
            "This ensures internal parity remains intact while reflecting the specialized expertise I bring to [Key Project].\n\n"
            "Best regards,\n[Your Name]"
        ),
        "verbal_script": (
            '"I understand and respect that you cannot disrupt internal band parity for current engineers. Let\'s keep the base salary at your band '
            'limit, but solve the gap through non-base levers: can we add a sign-on bonus, increase upfront equity, or put a written 6-month '
            'performance review in the offer letter?"'
        ),
    },
]


def get_all_objections() -> List[Dict[str, Any]]:
    """Return all recruiter objection playbooks."""
    return OBJECTION_PLAYBOOKS


def get_objection_by_id(obj_id: str) -> Dict[str, Any]:
    """Fetch specific objection playbook."""
    for item in OBJECTION_PLAYBOOKS:
        if item["id"] == obj_id:
            return item
    return OBJECTION_PLAYBOOKS[0]
