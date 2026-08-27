# BUILD STATUS — Constitution vs. what is actually in the repository

**SIH26102 · MPLADS AI Monitoring · Team Morior Invictus**
**Audited 2026-08-27 against the PROJECT CONSTITUTION dated 2026-08-24.**

Every figure below was read out of the working tree, not from any planning document. Where
the Constitution and the code disagree, the code wins and the disagreement is recorded.

> **The Constitution is stale in one important way.** §16 states that *"the real-data
> reframed modules (Phases 1–7) are specified but NOT yet implemented."* That is no longer
> true — all seven phases exist and run. It is also stale in the opposite direction: §2 and
> §3.3 list photo verification as *Synthetic/Future*, and it is now built on real records.
> Neither of those should be repeated to a judge as written.

---

## Headline

| | |
|---|---|
| **Overall completion against specified scope** | **~78%** |
| Fully delivered | UVP-1, UVP-3, UVP-6, ML stages 1/2/3/7, §7 killed-signals discipline |
| Materially incomplete | UVP-4 (30%), UVP-5 (45%), UVP-7 (50%), §10 evaluation (48%) |
| Not started | choropleth map, audit-plan screen, money-gap funnel, Docker |
| Built beyond the Constitution | field verification, OCR, perceptual hashing, auth/RBAC, audit log, chatbot, 10 languages |

| Section | Done | One-line verdict |
|---|---|---|
| §16 Phases 0–10 | **85%** | Every phase exists; 5 and 7 are thin |
| §2 PS requirement coverage | **85%** | Real-data rows almost all covered |
| §6 ML architecture (9 stages) | **78%** | Six complete, three partial |
| §13 Dashboard (8 screens) | **75%** | 6 of 8, plus 4 screens beyond spec |
| §5 UVP layer (7) | **71%** | The three soft spots are all here |
| §8 Tech stack (MVP rows) | **100%** | Postgres deliberately replaced by Parquet |
| §10 Evaluation | **48%** | **Weakest area in the project** |

---

## 1. UVP layer (§5) — 71%

### UVP-1 · Archetype-conditional forensic triage — **100%**

Everything the Constitution specifies is present and verifiable.

| Requirement | Status | Evidence in code |
|---|---|---|
| MiniLM description embeddings | ✅ | cached `all-MiniLM-L6-v2`, 384-d |
| Unsupervised archetype discovery | ✅ | `MiniBatchKMeans`, 187,865 descriptions |
| K chosen empirically, not hard-coded | ✅ | `train.py` silhouette sweep over K=20…60 → K=50 |
| Peer group = archetype × state × scale | ✅ | `pipeline.py` peer levels |
| Size floor + hierarchical back-off | ✅ | `config.MIN_PEERS`, `peer_level` recorded per work |
| Leave-one-out comparison | ✅ | `_loo_percentile()` — a work is genuinely not compared to itself |

Silhouette is **0.050** and is described everywhere as a separation measure, never accuracy,
exactly as §20 requires.

### UVP-2 · Completion-risk / time-to-event — **85%**

| Requirement | Status | Note |
|---|---|---|
| Survival model with right-censoring | ✅ | `lifelines` `CoxPHFitter`, censored at snapshot |
| Concordance index reported | ✅ | **0.6759** held out |
| Censoring anchor handled honestly | ✅ | anchored on `max(RECOMMENDATION_DATE)` = 2026-05-26 |
| **Left-truncation** (§21 Q2) | ❌ | Not modelled. Still an open team decision, as the Constitution predicted |
| Kaplan-Meier baseline per archetype × state | ❌ | Cox only |
| Calibration curve | ❌ | Not produced |

The language discipline §5 demands ("estimates completion probability", never "predicts which
projects will never complete") is honoured in the code comments, the API and the UI.

### UVP-3 · ₹ exposure at risk — **95%**

Computed as amount × completion risk, surfaced nationally (**₹1,302 Cr**) and broken down by
state. Correctly and repeatedly described as exposure, never loss. Breakdown by risk band and
archetype exists in the artifacts but is only partly surfaced in the UI.

### UVP-4 · Entity behavioural fingerprint — **30%** ⚠️

The Constitution specifies an eight-dimensional, time-varying vector per entity:

| Dimension | Built |
|---|---|
| work volume | ✅ |
| value distribution | ❌ |
| duration distribution | ❌ |
| activity / archetype mix | ❌ |
| completion rate | ❌ |
| anomaly rate | ❌ |
| templating rate | ❌ |
| back-dating rate | ❌ |

**Only monthly volume is implemented** (`temporal.entity_trends`). §9's `BehaviourProfile`
table is effectively unpopulated. This is listed in §22 as the project's "punch" UVP and is
currently the thinnest component in the system.

### UVP-5 · Behavioural change-point detection — **45%** ⚠️

| Requirement | Status | Reality |
|---|---|---|
| Detect that behaviour shifted | ✅ | `classify_series()` — 73 of 697 agencies flagged |
| CUSUM / Jensen-Shannon / `ruptures` | ❌ | A z-score + ratio-shift heuristic instead |
| Identify **when** it shifted (`change_date`) | ❌ | Not produced |
| Before/after distributions for a human | ❌ | Only a one-sentence explanation |
| §9 `ChangePoint` table | ❌ | Unimplemented |

The current method compares the last three periods against the series' own baseline. It is
defensible and honestly explained, but it is a **level-shift detector, not change-point
detection**, and it answers "something changed" rather than the Constitution's stated
question "*when* did this change?". This is where §19 Q15 ("why isn't this a GROUP BY?") is
hardest to answer.

### UVP-6 · Evidence fusion / investigation case file — **95%**

Noisy-OR fusion over independent families, the L1–L4 evidence ladder, confidence bands from
corroboration count, per-signal detail, verify-next, and an explicit non-fraud contract on
every case. Six families fire: amount, duration, lifecycle, behaviour, multivariate,
duplication.

### UVP-7 · Audit-ROI optimization — **50%** ⚠️

| Requirement | Status |
|---|---|
| Ranking by risk × ₹ × corroboration | ✅ `audit_roi = priority × rs_exposure × (1 + n_families)` |
| **Capacity budget** (e.g. 100 auditor-days) | ❌ no `capacity` or `budget` anywhere in `src/` |
| Recommended priority **plan** | ❌ |
| "₹-exposure covered within top-K" | ❌ |
| Sensitivity testing of weights | ❌ |

What exists is a ranking formula. What §5 and §22 claim is a **budgeted optimization** that
produces an approvable plan. The claim currently outruns the code.

---

## 2. ML architecture (§6) — 78%

| # | Stage | Type | Status |
|---|---|---|---|
| 1 | Description embedding | ML (pretrained) | ✅ 100% |
| 2 | Archetype discovery | ML (unsupervised) | ✅ 100% |
| 3 | Peer anomaly | Statistics | ✅ 100% |
| 4 | Completion-risk | Survival | 🟡 85% |
| 5 | Entity fingerprint | Data eng + stats | ⚠️ 30% |
| 6 | Change-point | Statistics | ⚠️ 45% |
| 7 | IsolationForest cross-check | ML (unsupervised) | ✅ 100% (4,220 flagged) |
| 8 | Evidence fusion | Rules + probability | ✅ 95% |
| 9 | Audit-ROI | Optimization | ⚠️ 50% |

The §6 discipline — never calling rules "AI" — is respected in code and UI copy.

---

## 3. Dashboard (§13) — 6 of 8 screens, 75%

| # | Screen specified | Status | Built as |
|---|---|---|---|
| 1 | National overview | 🟡 partial | `Overview` — **money-gap funnel missing** |
| 2 | State/district explorer, choropleth | ❌ **not built** | No map library in the project at all |
| 3 | Work-risk explorer | ✅ | `Worklist` (Investigation Queue) |
| 4 | Completion-risk / ₹ exposure | ✅ | `Compliance` + early-warning |
| 5 | Behavioural change timeline | 🟡 partial | `Trends` — no per-entity timeline with marked change-point |
| 6 | Investigation case file | ✅ | `CaseFile` |
| 7 | Audit prioritization plan | ❌ **not built** | Ranking exists; no budgeted plan screen |
| 8 | Methodology / transparency | ✅ | `Transparency` — killed signals, real-vs-future, limits |

**Beyond the specified eight:** `Landing`, `Login`, `Archetypes`, `Duplicates`, `HowItWorks`.

---

## 4. Roadmap (§16) — 85%

| Phase | Objective | Status |
|---|---|---|
| 0 | Data validation | ✅ 100% |
| 1 | Real-data adapter | ✅ 100% |
| 2 | Archetype discovery | ✅ 100% |
| 3 | Anomaly engine | ✅ 100% |
| 4 | Completion-risk | 🟡 85% — no left-truncation, no calibration |
| 5 | Behaviour / change-point | ⚠️ 40% — volume only, no change dates |
| 6 | Evidence fusion / cases | ✅ 95% |
| 7 | Audit optimization | ⚠️ 50% — no budget, no ₹-coverage@K |
| 8 | FastAPI backend | ✅ 100% — 29 endpoints |
| 9 | React dashboard | 🟡 80% — screens 1,3,4,6 done; 7 missing; 2 missing |
| 10 | Demo hardening | ✅ 90% — `docs/JUDGE_SCRIPT.md` |

---

## 5. Evaluation (§10) — 48% ⚠️ **weakest area**

| Module | Metric specified | Status |
|---|---|---|
| Archetypes | silhouette | ✅ 0.050, honestly framed |
| Archetypes | manual coherence review | ✅ 49 named, 1 declared uninterpretable |
| Anomaly ranking | precision@K | ✅ reported |
| Anomaly ranking | recall@N | ✅ reported |
| Anomaly ranking | **average precision (AP)** | ❌ |
| Anomaly ranking | **ablation study** | ❌ |
| Anomaly ranking | **stability across seeds** | ❌ |
| Anomaly ranking | **top-30 real-lead false-positive audit** | ❌ |
| Completion-risk | C-index | ✅ 0.6759 |
| Completion-risk | temporal holdout | 🟡 held-out split, not explicitly temporal |
| Completion-risk | calibration curve | ❌ |
| Change-point | recovery of synthetic injected changes | ❌ not in the harness |
| Audit-ROI | ₹-coverage within top-K | ❌ |
| Audit-ROI | vs random / complaint-driven baseline | ❌ |

**What does exist and is strong:** the synthetic injection harness — 904 planted anomalies,
**69.2% overall detection** (stalled 96.1%, inflated 83.2%, lifecycle break 58.0%, cloned
50.0%), with recall@k reported separately from detection and the difference explained. The
hard rule that synthetic metrics are never quoted as fraud rates is honoured.

**The gap that matters most:** §18 names the top-30 false-positive audit as the primary
false-positive mitigation, and §21 Q7 makes it the objective fallback trigger. It has not
been run, so that safeguard does not currently exist.

---

## 6. Tech stack (§8)

| Maturity | Specified | Built |
|---|---|---|
| **MVP** | Python, pandas/NumPy/SciPy, scikit-learn, sentence-transformers, lifelines | ✅ all present |
| Prototype | FastAPI | ✅ |
| Prototype | React | ✅ (React + Vite, not TypeScript) |
| Prototype | **PostgreSQL** | 🔄 **replaced by Parquet + JSON artifacts** (SQLite for audit log and field records) |
| Prototype | **ruptures / CUSUM** | ❌ not used |
| Prototype | **Leaflet / MapLibre** | ❌ not used |
| Prototype | **Docker** | ❌ not built |
| Optional | FAISS, OR-Tools, Polars | ❌ none (acceptable — marked optional) |

The Postgres → Parquet substitution is a **deliberate, defensible** call: the whole pipeline
runs in ~4 minutes on a laptop, so a database server earns nothing. Say so proactively rather
than letting a judge find the mismatch. **Note the submitted SIH deck says DuckDB, which is
also not used** — the same answer covers both.

---

## 7. Built beyond the Constitution

These are not in the Constitution and are real, tested code.

| Capability | Constitution says | Reality |
|---|---|---|
| **Field verification** | not mentioned | Built — immutable, attributed, timestamped records |
| **OCR of site boards** | not mentioned | Built — RapidOCR, ONNX, CPU-only, degrades to manual entry |
| **Perceptual photo hashing** | §2/§3.3 "Synthetic/Future" | **Built on real records** — pHash + dHash |
| RBAC / auth | §12 principle only | JWT, 4 seeded roles, server-side scope enforcement |
| Audit trail | §12 principle only | Hash-chained log with a verify endpoint |
| Multilingual | not mentioned | 10 languages, static bundles |
| Assistant | §19 Q14 cautions against LLM | 15 read-only tools, deterministic offline router, no arithmetic |
| Tests | 3 synthetic tests | **186 passing, 2 skipped** |

**Strategic note.** §3.2 states the project's central limitation: *"No fraud labels (none
exist publicly)."* Field verification records **are** those labels, accumulating one site
visit at a time. `field.label_readiness()` reports **3 of the ~500** needed before the fusion
weights in `config.SIGNAL_WEIGHTS` could be fitted rather than reasoned. Nothing is refitted
and no accuracy is claimed — which is the honest position, and a stronger story than the
Constitution currently tells.

---

## 8. Claim discipline (§20) — clean

No violation found in the shipped surfaces.

- No fraud verdicts, scores, or classifiers anywhere. Enforced by an automated test that
  greps the whole source tree and fails the build.
- No compliance check asserts `OFFICIAL_RULE`; all are `OBSERVED_BASELINE` or
  `STATISTICAL_OUTLIER`, and a test enforces it.
- `ACTUAL_AMOUNT` is never presented as expenditure; the 98.35% identity is measured and
  published on the Transparency screen.
- Silhouette is described as separation, never accuracy, in code, docs and UI.
- Synthetic metrics are labelled synthetic.

⚠️ **One live risk outside the app:** `origin/main` carries a root-level `chat.py` (added
2026-08-27) containing fabricated state figures, a non-existent `config.ARTIFACTS_DIR`, and
three checks declaring `"authority": "Statutory Rule"`. Nothing imports it, so the running
system is unaffected — but it violates §3.3 and §20-C and should be deleted before anyone
wires it up.

---

## 9. Priority order for the remaining work

Ranked by demo value per hour of effort.

| # | Gap | Why it matters | Size |
|---|---|---|---|
| 1 | **Money-gap funnel** on Overview | §11 demo step 2 promises it; the data is already computed | Small |
| 2 | **Top-30 false-positive audit** | §18's stated FP mitigation and §21 Q7's fallback trigger; answers §19 Q16 | Small |
| 3 | **Audit-ROI budget + ₹-coverage@K** | Turns a ranking formula into the decision-support claim §22 leads with | Medium |
| 4 | **Per-entity change timeline + change dates** | Screen 5 as specified; makes UVP-5 answer "when" | Medium |
| 5 | **Entity behavioural vector** (beyond volume) | UVP-4 is 30% built and is billed as the "punch" | Large |
| 6 | Choropleth explorer (Screen 2) | Visually strong, no new modelling required | Medium |
| 7 | Left-truncation + calibration curve | Closes §21 Q2 and hardens §19 Q7 | Medium |
| 8 | Docker | Only if one-command start is required for submission | Small |

**If only three are done before evaluation: 1, 2 and 3.** They are the cheapest, and each
one closes a gap between a claim already being made and what the code actually does.

---

## 10. Open team decisions (§21) — still open

| # | Question | Status |
|---|---|---|
| 1 | Archetype K and method | **Resolved** — K=50 by silhouette sweep, MiniBatchKMeans |
| 2 | Survival covariates & censoring anchor | **Partly** — anchor resolved; left-truncation still unhandled |
| 3 | Entity granularity for fingerprints | **Open** — agency used by default, never decided |
| 4 | Audit-capacity assumption | **Open** — blocks gap #3 above |
| 5 | Semantic-ring inclusion | **Resolved** — shipped as a visible secondary lead |
| 6 | Synthetic module posture | **Superseded** — photo verification is real now, not a preview |
| 7 | Fallback trigger to A³ (26056) | **Open** — threshold never set, and the FP audit it depends on has not run |
