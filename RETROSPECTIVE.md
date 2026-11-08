# Launch Retrospective — India Salary & Career Intelligence Platform (Offer Evaluator)

**Window:** [Start Date] → [End Date]  
**Effort:** ~[N] hours, solo  
**Status at close:** [shipped / iterating / parked]  

---

## 1. What I set out to test

The hypothesis, stated before launch:

> Indian tech workers evaluating an offer will use a single-screen tool that converts CTC to monthly in-hand bank credit and shows their peer percentile with calibrated conformal prediction bounds, and enough of them will submit their own data anonymously to make the next user's percentile more accurate.

The number I said would mean **"keep going"**: **20 evaluations/week sustained without a new post**.  
The number I said would mean **"stop and rethink"**: **<5 evaluations/week**.  
*(Written down before launch so I can't move the goalposts later).*

---

## 2. The numbers

| Metric | Target | Actual | Verdict |
|---|---|---|---|
| Evaluations (total) | — | | |
| Evaluations / week (steady state) | 20 | | |
| Unique visitors | — | | |
| Evaluations per visitor | — | | |
| Submission rate (submitted / evaluated) | 10% | | |
| Share-card clicks | — | | |
| Share-card clicks → new visit (if trackable) | — | | |
| p50 time-to-first-result | <2s | | |

**The one number I care about most:** Evaluations/week  
**What it was, and whether it met the bar I set:**  

---

## 3. What actually happened

Shortest honest version, 3–5 bullets. Not the launch-day story — the shape of the six weeks.

- [e.g. "The r/developersIndia post drove 1,400 visits in 48 hours, then settled to ~9 evaluations/week from organic + WhatsApp shares."]
- [e.g. "Submission rate was 14% for offer-evaluation traffic, but 0% for visitors who used only the in-hand calculator."]
- [e.g. "The WhatsApp share card was clicked on 28% of evaluations — higher than expected, and became the sole source of new inbound visits after week 1."]

---

## 4. What I got wrong

This section is the point of the document. If it's empty, I didn't launch hard enough.

| Assumption | What I believed | What was true | Cost |
|---|---|---|---|
| [e.g. Offer evaluator is the sole wedge] | [Users only want the verdict] | [60% of mobile traffic just wanted the in-hand breakdown] | [Refactored hero to show in-hand bank credit above the fold] |
| | | | |

**Biggest wrong assumption, one paragraph:**

---

## 5. What I got right

Equally short. These are the decisions I'd repeat on the next project.

- [e.g. "Leading with the cross-validated figure (0.50 ± 0.06) instead of the holdout (0.57) meant nobody in the Reddit thread accused me of cherry-picking. The discussion stayed technical."]
- [e.g. "Server-rendered 1080x1080 share card worked seamlessly in WhatsApp previews with zero client-side canvas bugs."]
- [e.g. "Cutting tabs 2–4 and focusing on a single question allowed shipping the core tool in one sitting."]

---

## 6. What I would do differently

One paragraph, no hedging. Written for the version of me starting the next project.

---

## 7. Where it stands now

- **Code:** [What's live, what's dead, what's hidden]
- **Data:** [N submissions collected; N verified domains; is it worth anything to a user yet?]
- **Model:** [5-fold CV R² = 0.4993 ± 0.0620; did new submissions change it? If not, say so — that's fine, it was never the point]
- **Known weaknesses:** [Be specific. E.g. "Company coverage is still 118 firms; roles outside the 15 canonical families fall back to domain priors."]

---

## 8. Decision: ship, iterate, or park

**Decision:** [ship / iterate one more cycle / park]

**Why:** [2–3 sentences. If "ship": what's the threshold I hit? If "iterate": what's the one thing I'm changing, and by when is it either working or parked? If "park": what did I learn that carries to the next thing?]

---

## 9. What this project proves I can do

For interview use. 3–4 sentences, concrete, no adjectives that a technical person would challenge.

- "Built and shipped an ML-backed web tool end-to-end: data cleaning → regex taxonomy → 5-fold CV evaluation → conformal prediction → Streamlit / FastAPI service → server-rendered share cards."
- "Audited my own prediction intervals, diagnosed that tree variance under-covered at 71.2% empirical coverage against an 80% nominal target, implemented split conformal prediction on out-of-fold residuals (±6.01 LPA margin), and published the methodology."
- "Shipped a data-driven product to [N] real users and collected [N] crowdsourced records in six weeks at 10 hrs/week."

---

## 10. What this project proves I *can't* yet do

Also for interviews. Honesty here is what makes section 9 land.

- "I have not worked on a large team codebase, a formal code review cycle, or a distributed system serving thousands of concurrent requests."
- "My ML experience is tabular regression on mid-sized datasets — not deep learning, distributed training, or massive streaming feature stores."

---

*Filed: [Date]. Next review: [Date, or 'None — Shipped'].*
