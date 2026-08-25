# What we built — in plain English

**Project:** MPLADS AI Forensic Monitoring & Decision Support · SIH 2026 · PS 26102 (MoSPI)
**Team:** Morior Invictus

---

## The problem, simply

Members of Parliament recommend small local development works — roads, community halls,
street lights, water tanks, borewells. There are **over 2,10,000** of them across the
country, worth about **₹11,565 crore**. No official can inspect them all by hand. Today,
finding the works worth a closer look is slow and mostly reactive.

## What we made

A system that reads **every** work and produces a short, ranked list of the ones that look
unusual compared to **genuinely similar works** — so limited audit time goes where the most
money is at risk. It comes with a clean web app anyone can use.

**One rule we never break:** the system produces **investigation leads, not verdicts**. It
never says "this is fraud." It says "a human should check this, and here is exactly why."

---

## How it works, in five steps

1. **Learn what normal looks like.** The computer reads each work's description and groups
   similar works together (roads with roads, halls with halls). It found **50 natural
   groups** ("archetypes") on its own.

2. **Compare each work with its true peers.** For every work we find similar works in the
   same state and of the same type, then ask: is this one unusually expensive, or taking
   unusually long, compared to *those* peers? (Being different from the national average is
   not enough.)

3. **Predict which works may not finish.** Many works are still ongoing. Using the history
   of how long similar works took, the model estimates how likely each unfinished work is
   to stall. The money tied up in at-risk works is called **"exposure at risk."**

4. **Notice when behaviour changes.** For each implementing agency we watch how their
   pattern of works shifts year to year. A sudden change is worth a look — though it can
   have an innocent reason (a new officer, a rule change).

5. **Explain and prioritise.** A work is only raised when **at least two independent kinds
   of evidence agree** — never on a single hunch. Each raised work becomes a plain **case
   file** listing why, plus the one thing a human should check next. The list is ranked so
   the biggest money-at-risk is on top.

---

## The models we actually trained

Three models were trained on the real data. (The tool that turns text into numbers,
"MiniLM," is a standard pre-built component — we reuse it, we don't train it.)

| Model | What it does | Honest result |
|---|---|---|
| **Work grouping** (MiniBatchKMeans) | Sorts 1.88 lakh descriptions into 50 archetypes | We tested 5 group counts; 50 was clearest. "Clarity" score ≈ 0.05 — this is a *separation* measure, **not accuracy**, and we say so plainly |
| **Completion risk** (Cox survival model) | Estimates which works may not finish on time | **68% ranking accuracy** (concordance) on held-out data — honestly reported, correctly handling works that are simply still in progress |
| **Outlier detector** (IsolationForest) | Flags works with an unusual money-and-age profile | **4,220 works** flagged as one extra corroborating clue, never as proof |

---

## What the system found

| Number | Meaning |
|---|---|
| **2,10,993 works** monitored | The full national portfolio |
| **₹11,565 crore** recommended | Total value of all works |
| **₹1,482 crore** exposure at risk | Money in works that may not finish — *not* proven loss |
| **22,687 investigation leads** | Works where ≥2 kinds of evidence agree |
| **2,513 high-confidence leads** | Works where 3+ independent kinds of evidence agree |
| **36 states · 545 constituencies · 778 agencies** | National coverage |

A real example the system surfaced: a **₹6.5 crore outdoor-gym batch in Saran, Bihar** —
its amount is at the very top of 144 similar works, it has been open longer than all its
peers, the survival model rates it high-risk, and the agency's pattern shifted. Four
independent clues agree, so it ranks near the top. The recommended step: *a human should
verify the scope and estimate with the Implementing Agency.*

---

## What we are careful **not** to claim

- We do **not** call anything fraud. There are no fraud records in this public data to
  learn from, so any "fraud detector" would be invented.
- The grouping "clarity" score (≈0.05) is a **separation measure, not accuracy**.
- **"Exposure at risk" is money that *could* be tied up** in works that may not finish — it
  is not proven loss or missing money.
- Every case ends with **"a human should check…"**. People decide; the computer only points.

---

## What you can click through

The web app has four screens, written for a non-technical reader:

- **Overview** — the national picture: totals, money at risk, a map of exposure by state,
  and the 50 learned work types.
- **Audit Worklist** — the ranked list of leads, searchable and filterable, most
  money-at-risk first.
- **Case File** — open any lead to see its evidence, its peer comparison, its completion
  risk, and the recommended human action. This is the heart of the product.
- **How it works** — this same explanation, built into the app.

---

## What is done vs. still open

**Done and working end-to-end:** data ingestion, the three trained models, peer comparison,
completion risk, evidence fusion, ranked case files, the REST API, and the full web app.
The whole thing runs from raw files to a live dashboard.

**Still worth adding (for a submission, not a demo):** a formal validation report (planting
known odd cases and checking the system catches them), login/roles and a tamper-proof audit
log on the API, and Docker packaging. None of these change what the demo *does* — they are
hardening and proof.

## Run it yourself

```bash
mplads ingest      # build the clean data tables
mplads train       # train the three models (~90 seconds)
mplads pipeline     # produce the ranked case files (~15 seconds)
mplads api          # serve it at http://127.0.0.1:8000
```
```bash
cd frontend && npm run dev   # the web app at http://localhost:5173
```
