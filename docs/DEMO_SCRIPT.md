# Demo script — 4 minutes

**Setup (before you present):**

```bash
cd C:/Users/kanna/Downloads/MPLADS && .venv/Scripts/python.exe -m uvicorn mplads.api.app:app --port 8000
```
```bash
cd C:/Users/kanna/Downloads/MPLADS/frontend && npm run dev
```

Open the app, set the role selector to **Ministry (MoSPI)**, and start on **Overview**.

---

## Step 1 · Scale (25s) — Overview

> "This is every MPLADS work in the country — **2,10,993 works, ₹11,565 crore**, across 36
> states, 545 constituencies and 778 implementing agencies. All of it real government data
> from the eSAKSHI portal. No official can read 2 lakh works. Our system read all of them."

Point at **₹1,482 crore exposure at risk** and say what it is *not*: "that is money tied up
in works that may not finish — not proven loss."

## Step 2 · Semantic understanding (30s) — Work Archetypes

> "Nobody told the system what kinds of work exist. It read every description, turned each
> into a 384-number semantic fingerprint, and discovered **50 work archetypes** on its own —
> street lighting, CC roads, community halls. The labels come from the actual cluster
> contents; we invent nothing."

Show the completion rate and lead rate varying by archetype: "different work types behave
differently, which is exactly why comparing a road to a road matters."

## Step 3 · Temporal intelligence (30s) — Temporal Intelligence

> "The system watches how the scheme changes over time. **64 agencies show a persistent
> shift** in behaviour and **9 a sudden change**. The Emerging Works Radar shows which
> categories are growing and declining."

Say the honest bit: "we deliberately use recommendation-time data only — completion-based
series would make every recent month look 'changed' purely because works haven't had time
to finish."

## Step 4 · Duplicate detection (35s) — Near-Duplicates

> "We found **223,407 semantically similar pairs**. But repeated descriptions are normal —
> one MP recommending forty street lights writes the same sentence forty times. So we narrow
> to pairs that are near-identical **from the same agency for the same amount** — the shape a
> repeated claim would take. That leaves **47,709 pairs** worth a human's eye."

This is the strongest "we understand the domain" moment. Do not skip the caveat.

## Step 5 · The case file (60s) — Investigation Queue → click the top row

> "The queue is ranked by Audit-ROI — priority × money at risk × corroboration. Nothing is
> surfaced on a single signal; a work needs **at least two independent evidence families**."

Open the top case and walk the evidence:
- **Peer amount** — at the 100th percentile of 144 comparable works
- **Completion risk** — from a trained Cox survival model
- **Early warning** — how many times longer it has been open than its peers
- **Compliance findings** — each tagged *Observed baseline* or *Statistical outlier*
- **Recommended next step** — always "a human should…"

> "Every number on this screen carries its explanation. An officer never sees a bare score."

## Step 6 · Role views (25s) — role selector

Switch **Ministry → State Nodal (Bihar) → District → MP**.

> "One intelligence layer, four stakeholder views. The Ministry sees the nation; a State
> Nodal Officer sees their state; a District Authority sees their jurisdiction. This is role
> simulation — we're honest that authentication isn't implemented in the prototype."

## Step 7 · The differentiator (45s) — Data Transparency

> "This is what separates us. The problem statement asks for expenditure analysis, cost
> overruns, payment tracking and photo verification. **None of that data is published.**"

Show the three columns — Measured / Derived / Unavailable — then:

> "`ACTUAL_AMOUNT` looks like expenditure. We measured it: **98.35% of completed works have
> it exactly equal to the recommended amount**, and all but one of the rest differ by parts
> per million. It is a completion confirmation, not a spend record. So we refuse to build a
> cost-overrun model on it. We show what we can prove and declare what we cannot."

Finish on **Ready for restricted government data**:

> "The schema already carries typed interfaces for expenditure, tranches, cost estimates and
> geotags. The day MoSPI grants that data, they plug in — nothing is rebuilt."

## Step 8 · Close (20s)

> "Three trained models — clustering, a Cox survival model at 0.676 concordance, and an
> anomaly detector. 82 automated tests. Runs end-to-end from raw CSVs in under two minutes.
> And it never once calls anyone a fraud — it produces investigation leads with evidence,
> and a human decides."

---

## The three hardest questions, with honest answers

**"What's your fraud detection accuracy?"**
> "We don't claim one, and anybody who does on this data is fabricating it. There are no
> fraud labels in any public MPLADS source, so a supervised fraud model would have nothing
> to learn from. We report what we *can* measure: 0.676 held-out concordance on completion
> risk, and cluster separation of 0.05 — which is a separation metric, not accuracy."

**"Your silhouette score is only 0.05 — isn't the clustering bad?"**
> "It's low, and we publish it rather than hide it. MPLADS descriptions form a continuous
> semantic space, not clean separated blobs — we confirmed that by testing HDBSCAN, which
> rejected 80% of the data as noise. The clusters earn their place through downstream
> usefulness and manual coherence, not that number."

**"How do you know your leads are real without labels?"**
> "We don't validate against fraud, because we can't. What we validate is the machinery: the
> corroboration rule means nothing surfaces on one signal, every lead shows its evidence, and
> a synthetic planted level-shift is detected by the trend engine in our test suite. We're
> claiming a triage system that puts the right 4,478 works in front of a human — not an
> oracle."
