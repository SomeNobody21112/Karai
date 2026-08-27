# Judge Evaluation Script — MPLADS AI Forensic Monitoring

**Team Morior Invictus · SIH 2026 · PS SIH26102 (MoSPI)**

Everything here is written to be said **out loud, in plain language**. Technical terms are
introduced only after the plain-English version, never before.

Read the box below, then work top to bottom. Total runtime **8–10 minutes**, or **4 minutes**
if you only do the steps marked ⭐.

---

## 0. Before the judges sit down — 3-minute checklist

| # | Do this | Why |
|---|---|---|
| 1 | Kill stale servers | Old servers from a previous session hold ports 5173/5174/8000 and you will demo the *wrong build* |
| 2 | Start the API | Every screen is empty without it |
| 3 | Start the frontend | Note the port it prints |
| 4 | Open the landing page and **hard-refresh** (`Ctrl+Shift+R`) | Clears an old cached bundle |
| 5 | Set language to **English** | A previous session may have left it on Tamil |
| 6 | Log out / open a private window | So you can demo the login screen |

**Kill stale servers:**

```bash
taskkill /F /IM node.exe /IM python.exe
```

**Terminal 1 — the API:**

```bash
.venv\Scripts\python.exe -m uvicorn mplads.api.app:app --port 8000
```

**Terminal 2 — the website:**

```bash
cd frontend; npm.cmd run dev
```

> Use `npm.cmd`, not `npm`. PowerShell's execution policy on this machine blocks the
> `npm.ps1` shim and you will get a red `UnauthorizedAccess` wall in front of the judges.

Then open **http://localhost:5173**.

**Sanity check before they arrive:** the four numbers on the landing page must read
`2,10,993` · `₹11,565 Cr` · `4,478` · `50`. If any of them say `0`, the API is not running.

---

## The one-sentence answer

If a judge gives you only ten seconds, say exactly this:

> **"Two lakh public works exist. An official can realistically check a few hundred. We read
> all of them, compare each one against genuinely similar works, and hand over a short ranked
> list of what deserves attention — with the reason attached to every single item. We never
> say anyone committed fraud. We say where a human should look first."**

---

## 1. ⭐ The landing page — the problem, in human terms

**Open:** `http://localhost:5173`

### Say this

> "Members of Parliament each get a budget to recommend local works — roads, community halls,
> street lights, water tanks. There are **2,10,993** of them in this data, worth
> **₹11,565 crore**.
>
> Now imagine you are the officer responsible for checking them. If you spent just **one
> minute** on each work and did nothing else all day, it would take you **over a year** to
> look at every work once. That is not a staffing problem you can hire your way out of. It
> is an arithmetic problem.
>
> So today, monitoring is **reactive** — you look after something has already gone wrong.
> Our system makes it **proactive**."

### Scroll down slowly and narrate the five steps

The page itself lays out the whole method. Read them out:

> "**Learn → Compare → Predict → Explain → Prioritise.** Five steps, and every one of them
> can be explained to somebody who has never seen a line of code."

**Point at the Lego analogy on screen** (it is already written there):

> "Step one is like tipping out a giant box of mixed Lego and sorting it into piles — wheels,
> flat pieces, roof pieces — without anybody telling you those piles exist. The system read
> every work description and discovered **50 types of work** entirely on its own."

**Point at the school-bag analogy:**

> "Step two: to know whether you overpaid for a school bag, you compare it to other school
> bags in your town — not to every object in the shop. We compare a road to roads in the same
> state, not to the national average of everything."

---

## 2. ⭐ Login — who is allowed to see what

**Open:** `/login`

### Say this

> "Public money data is sensitive. A district officer should not browse another state's
> works. So the system has **role-based access** — four kinds of user, each seeing only their
> own jurisdiction."

**Log in as `auditor` / `mplads2026`.**

| Username | Who they are | What they see |
|---|---|---|
| `ministry` | MoSPI Programme Division | Everything, nationally |
| `auditor` | CAG Audit Officer | Everything, audit-focused |
| `bihar` | Bihar State Nodal Officer | Bihar only |
| `saran` | Saran Constituency Office | Saran constituency only |

> "The passwords are shown on screen deliberately, because this is an evaluation build. A
> real deployment plugs into the government's own identity system and would never list
> accounts like this. We say so on the screen rather than hiding it."

**If a judge asks "is that real security?"**

> "The token is a signed JWT and every request is checked against the user's scope on the
> server, not in the browser — so you cannot get another state's data by editing the URL.
> What is *demo-grade* is the account list and the shared password, and we label it as such."

---

## 3. ⭐ National Overview — the whole country on one screen

**Open:** `/overview`

### Say this, pointing at each of the four boxes

> "**Works monitored** — 2,10,993, of which 85,773 are finished and 1,25,220 are still open.
>
> **Total recommended** — ₹11,565 crore across 36 states and 778 implementing agencies.
>
> **Exposure at risk** — ₹1,302 crore. This is the number I most want to explain properly."

**This is the single most important concept in the product. Slow down here.**

> "Exposure is **not** money lost. It is **not** money stolen. Nobody has alleged anything.
>
> It is: *the sanctioned amount, multiplied by the probability that this work does not finish
> in the next year.* If a ₹10 lakh work has a 30% chance of stalling, that is ₹3 lakh of
> exposure.
>
> It answers a question an auditor actually has: **'if I can only chase some of these, where
> is the most public money hanging in the balance?'**"

> "**Investigation leads** — 37,705 works were surfaced. Of those, **4,478 are high-confidence**,
> meaning three or more *independent* kinds of evidence agreed."

### The confidence-bands chart — point at the colours

> "Red, amber, green — the same language as a traffic light.
>
> **Red/HIGH** means three or more independent signal families agreed. **Amber/MEDIUM** means
> two. **Green/LOW** means one — and one signal on its own is usually just noise.
>
> Notice each one also has its own **shape** — a triangle, a diamond, a circle. That is
> deliberate: roughly one man in twelve is red-green colourblind, and this is a government
> tool. Nobody should have to see colour to read it."

### The "learned work archetypes" table

> "These 50 categories were not written by us. The system discovered them from the text."

---

## 4. ⭐ Investigation Queue — the screen an officer actually works from

**Open:** `/worklist`

### Say this

> "This is the product. Everything else supports this screen.
>
> Two lakh works became a **ranked list**, and the ranking is by something we call
> **Audit-ROI** — audit return on investment."

**Point at the sub-heading, which shows the formula:**

> "Audit-ROI = priority × exposure × corroboration.
>
> In plain terms: **how odd is it**, times **how much money is at stake**, times **how many
> independent signals agree**. An inspector has a finite number of days and a travel budget.
> This ranks by where a day of their time is worth the most."

### Now click any row — it expands in place

> "Every single item opens up and tells you *why* it is here. No black box. The peer group it
> was compared against, its completion risk, and the evidence."

### Then open a full case file

Click **Case File →**.

---

## 5. ⭐ The Case File — the heart of the demo

**Open:** any case, e.g. `/case/MP3018356-W86316`

### Say this

> "This is what an officer receives. Read the plain summary at the top — it is written in
> ordinary English, on purpose:
>
> *'This work was put on the audit list because N independent kinds of evidence agreed
> something is worth checking. About ₹X may be tied up if it does not finish.'*"

### Walk the evidence panel

> "Each line is one piece of evidence, and each comes from a **different family** — a
> different way of looking at the work. Amount, duration, lifecycle, behaviour, statistical
> outlier, duplication.
>
> Why does that matter? Because if one method is wrong, the others are still independent. One
> signal is a coincidence. Four signals agreeing is worth an afternoon of somebody's time."

### The peer context panel

> "'Amount percentile: 98th' means: out of a hundred genuinely similar works, this one costs
> more than 98 of them. Not more than the national average of everything — more than its
> **true peers**."

### The closing line — do not skip it

> "And every case file ends the same way: **a recommended next step for a human.** Never a
> verdict. The system's job is to end the sentence with 'a human should check X'."

---

## 6. Field Verification — the loop closing

**On the same case file, scroll to Field verification.**

This is the newest and most impressive part. Full detail in `demo/WALKTHROUGH.md`.

### Say this

> "Everything I have shown you ends at *'a human should go and look'*. This is the only screen
> that records **what the human found when they went**."

### Four things to show, in order

**1. It reads the board.** Upload `demo/photos/01-board-matches.png`.

> "MPLADS already requires a display board at every work site. The officer photographs it.
> The system reads the work reference and the sanctioned amount straight off the board —
> nobody types a reference number while standing in a field."

**2. It notices a board for the wrong work.** Upload `demo/photos/02-board-different-work.png`.

> "The reference on the board does not match the case file we are standing in, and it says so
> **before** saving, not after."

**3. ⭐ It catches a recycled photograph.** Upload `03-photo-first-submission.png` on
`MP3017167-W136962`, save, then upload `04-photo-resubmitted.jpg` on `MP3017167-W136963`.

> "That is a **different file** — different name, different format, different size, a
> completely different cryptographic checksum. Re-saving an image defeats a normal checksum.
>
> We use a **perceptual hash**, which answers a different question. A normal hash asks 'is
> this the same *file*'. A perceptual hash asks 'is this the same *picture*' — and it survives
> re-compression, resizing, cropping and brightening.
>
> This is the one check a human genuinely cannot do at scale. Nobody remembers a photograph
> they approved eight months ago in a different district."

**Then say the honest line — judges reward this:**

> "And it is a **question, not a finding**. Two phases of the same road legitimately look
> identical from the roadside. The system asks; a human answers."

**4. ⭐ It admits when it is not sure — and this is the honest one.** Upload
`05-board-weathered.png`.

> "Faded and out of focus, the way boards actually look. Now watch what it does *not* do.
>
> It reads a work reference at 99.6% confidence — and that confidence is real, but it is
> confidence in the **pixels**, not in the answer. One digit is wrong. And because MPLADS
> reference numbers run in sequence, the wrong one is also a real work: two gym
> installations at two schools in the same block, with the same sanctioned amount. Character
> confidence cannot tell them apart. Neither can the amount.
>
> So it does not settle it. It shows every real work that differs by one character, says the
> reader cannot choose between them, and will not let the officer save until they confirm
> which board they actually photographed.
>
> A system that guessed here would be right most of the time and silently, confidently wrong
> the rest. We would rather ask."

### Why this matters most (the strongest point in the whole demo)

> "Here is the deepest problem with this entire problem statement: **there are no fraud labels
> in this data.** Nobody has ever marked a row 'this one was fraudulent'. So no honest system
> can be trained to predict fraud, and no honest team can claim an accuracy percentage.
>
> These verification records are **exactly those missing labels** — accumulating one site
> visit at a time. At about 500 of them, our scoring weights stop being reasoned defaults and
> start being fitted to what officers actually confirmed.
>
> The Data Transparency screen shows the running count and how many are still needed — and
> it excludes the demonstration records seeded for this walkthrough from that number, so
> nothing on this stage inflates it."

---

## 7. Temporal Intelligence — has behaviour changed?

**Open:** `/trends`

> "Two questions: is the country's spending pattern shifting, and has any single implementing
> agency changed how it behaves?
>
> **73 agencies out of 697** show a genuine change-point — a statistical break where their
> behaviour before and after is measurably different.
>
> Green means normal or stable. Amber means a gradual drift. Red means a sudden break.
> A sudden break is not wrongdoing — a new officer, a new scheme, a flood. It means
> *something changed, go and ask what.*"

---

## 8. Near-Duplicates — the same work claimed twice?

**Open:** `/duplicates`

**This is a great screen for showing judgement rather than brute force.**

> "We found **2,23,407** pairs of works with near-identical descriptions. And then we threw
> almost all of them away. Here is why.
>
> Repeated descriptions are completely **normal** in this scheme. One MP recommending forty
> street lights writes the same sentence forty times. If we flagged all of those, we would
> bury the officer in noise and they would stop using the tool by Tuesday.
>
> So a pair only counts as concerning when it is near-identical **and** from the **same
> implementing agency** **and** for a **near-identical amount**. That is the shape a repeated
> claim would actually take. That takes 2,23,407 down to **47,709**."

---

## 9. Compliance & Early Warning — and the honesty rule

**Open:** `/compliance`

> "Two things here. Stalling risk, graded critical/high/medium/low. And lifecycle compliance
> checks.
>
> Now look at the **Authority** column, because this is the difference between a defensible
> system and one that gets thrown out of court."

**Point at the three authority levels:**

> "Every check declares where its authority comes from:
> **Official rule**, **Observed baseline**, or **Statistical outlier**.
>
> And we assert **no official rules at all** — because no statutory threshold ships with this
> public data. If we called a statistical outlier a legal breach, we would be inventing law.
> There is an automated test in our codebase that fails the build if anyone ever tries."

**The Health Index:** 62.9 / 100.

> "A single operational health score, with every component and its weight shown. Notice the
> bars are graded — green where the system is healthy, red where it is not. You can see what
> pulled the score down instead of just being handed a number."

---

## 10. ⭐ Data Transparency — the screen that wins arguments

**Open:** `/transparency`

**If judges are technical or sceptical, this is your strongest screen. Do not skip it.**

> "This screen lists what we measure, what we derive, and — most importantly — **what this
> data simply does not contain.**
>
> Green means measured straight from government records. Amber means we computed it, with the
> confidence stated. Red means **unavailable, and we refuse to fake it.**"

### Then say the four honest limitations out loud

> "Four things this data cannot support, which we could easily have faked and did not:
>
> **1. We cannot do expenditure analysis.** There is a column called ACTUAL_AMOUNT. It looks
> like spending. It is not. On **98.35%** of completed works it is *exactly equal* to the
> recommended amount, and not a single work exceeds 1.05 times it. So there is no cost-overrun
> signal in this data. We measured that rather than assuming it.
>
> **2. There is no sanction date.** The sanction rows copy the recommendation date verbatim on
> **100%** of 1,79,676 works. We can prove a sanction *happened*; its timing is unknowable.
>
> **3. There is no district column.** So we make no district-level claims.
>
> **4. There is no cost estimate anywhere**, so no overrun detection is possible.
>
> Every one of those is on the screen with the measurement that proves it, and the code
> already has typed, empty interfaces ready if MoSPI grants the richer data."

---

## 11. Work Archetypes & How It Works

**Open:** `/archetypes`

> "The 50 work types, with the distinctive terms that define each one. Forty-nine got a name.
> **One is labelled 'not interpretable'** — because that cluster is held together by language
> rather than by work type, and saying so is better than inventing a name."

**Open:** `/how` — the illustrated method walkthrough, useful if a judge wants the pipeline again.

---

## 12. ⭐ The chatbot — ask it anything

**Click the ◈ button, bottom-right, on any screen.**

Ask: **"How many investigation leads are there?"**

It answers, correctly:

> *"37,705 works were surfaced for review — 4,478 at HIGH confidence (three or more
> independent signal families agreed) and 33,227 at MEDIUM (two)."*

### Say this

> "Notice the little tag under the answer — it shows **which data tool** it used to get that
> number. There are **ten read-only tools**.
>
> The important part: this assistant **cannot do arithmetic and cannot browse.** It can only
> look things up in results our deterministic pipeline already computed. It physically cannot
> invent a figure, because it has no way to produce one."

**Also demo the language switcher** — pick हिन्दी or தமிழ்.

> "Ten languages. And the interface translation is a **static table**, not a live AI call —
> because a demo must never depend on a paid network request."

---

## 13. The technical section — if judges ask for depth

### The three trained models, in plain English first

| Model | Plain English | Technical | The honest number |
|---|---|---|---|
| **Work archetypes** | Sorts 1,87,865 descriptions into 50 piles of similar work | MiniBatchKMeans over `all-MiniLM-L6-v2` sentence embeddings, 384 dimensions, K chosen by sweep | Silhouette **0.050** |
| **Completion risk** | Predicts which works are likely to stall | Cox proportional-hazards survival model (`lifelines`), right-censored at snapshot, 365-day horizon | C-index **0.6759** held out |
| **Odd-one-out detector** | Spots works unusual on several measures at once | IsolationForest over standardised `[log_amount, age_days]`, contamination 0.02 | **4,220** flagged |

### ⚠️ Say the silhouette line before a judge catches you

> "Our clustering silhouette is **0.050**. I want to say clearly what that is and is not.
>
> Silhouette measures how *separated* clusters are. It is **not accuracy**. Real-world text
> clusters overlap heavily — a 'community hall' and a 'community centre' genuinely are close.
> A high silhouette on this data would mean we had cherry-picked easy clusters.
>
> We report it honestly in the UI, in our code comments and in our docs, rather than hiding
> it. And this is exactly why archetypes are a **secondary** signal for us. Our main peer
> comparison uses the official government category, which is far more defensible."

**That last point is worth its own moment:**

> "The `ACTIVITY_NAME` field looks unusable — it has 1.8 lakh distinct values. Both the
> problem-statement deck and the previous team wrote it off. But it is a **composite string**:
> `WS/MP519/2023-2024/49391-Installation of multi-gym equipment`.
>
> Split it on the dash and you get **118 official government categories covering 93% of
> works.** That gave us a free, interpretable, unimpeachable way to group peers. Nobody had
> split the field."

### The C-index line

> "C-index 0.6759 means: given two works, the model ranks which one finishes sooner correctly
> about **68%** of the time. Better than a coin toss, not magic. And it is a *completion-time*
> model — never a probability of wrongdoing."

### How the signals combine

> "Six independent signal families feed a **noisy-OR fusion** — a standard way of combining
> evidence that assumes the signals are independent and never lets one loud signal dominate.
> The weights are transparent constants in a config file, not learned, because there are no
> labels to learn from. You can read them and disagree with them."

### The architecture, top to bottom

Straight from our submitted deck:

```
DATA — eSAKSHI / MPLADS      210,987 works · 476,781 lifecycle events
   ↓
VALIDATION & FEATURES        schema + date checks · censoring anchor
   ↓
SEMANTIC REPRESENTATION      MiniLM 384-d → 50 archetypes
   ↓
PEER COMPARISON              same-state k=100 kNN · per-unit price
   ↓
RISK + BEHAVIOUR             Cox PH completion risk · change-points
   ↓
FUSION → ₹ EXPOSURE          noisy-OR across independent families
   ↓
AUDIT-ROI                    finite inspector-day and travel budget
   ↓
OUTPUT — CASE FILE           investigation leads, never fraud findings
   ↓
SERVING                      FastAPI · read-only
```

### The stack

- **Data & ETL:** Python 3.11 · pandas · NumPy · Parquet
- **Embeddings:** Sentence-Transformers `all-MiniLM-L6-v2` (384-d)
- **Models:** scikit-learn (MiniBatchKMeans, IsolationForest) · lifelines (Cox PH)
- **API:** FastAPI, with JWT role-based access and a hash-chained audit log
- **Field layer:** RapidOCR (ONNX, CPU-only) · perceptual hashing (pHash + dHash)
- **Frontend:** React + Vite + Recharts, 10 screens, 10 languages
- **Tests:** ~160 automated tests

> ⚠️ **One correction to make if asked:** our submitted deck lists **DuckDB**. We
> ended up using **pandas + Parquet** instead — the whole pipeline runs in about four minutes
> on a laptop, so a separate analytical database earned nothing. Say this proactively if a
> judge has the deck open; it reads as engineering judgement, not as a gap.

> ✅ **Also worth saying:** the deck marked *"React dashboard · containerisation · RBAC + audit
> log"* as **PLANNED — NOT BUILT**. The React dashboard and RBAC + audit log are now **built
> and in front of you.** Containerisation is the one item still outstanding.

---

## 14. How we prove it works with no labels

**If a judge asks "how do you know any of this works?" — this is the answer.**

> "You cannot measure accuracy without labels, and we have none. So instead we **planted
> anomalies we designed ourselves** into the real data, and measured how many the system
> caught blind.
>
> Overall detection: **69.2%**. Broken down:
> - Stalled works: **96.1%**
> - Inflated amounts: **83.2%**
> - Lifecycle breaks: **58.0%**
> - Cloned works: **50.0%**"

### The trap question — be ready for it

If a judge notices recall@5000 looks low (14.8%):

> "That is correct behaviour, and I am glad you asked. Detection and *ranking* are measured
> separately on purpose. Audit-ROI multiplies by rupee exposure — so a planted anomaly inside
> a ₹3 lakh work **should** rank below a genuine ₹6 crore one. An auditor with ten days wants
> the ₹6 crore work first. We report both numbers and explain the difference rather than
> quoting only the flattering one."

### "We tried to break it — and did"

This is on the submitted deck and judges love it:

> "Batch works were **4.03× over-represented** in our top 200 leads. We were comparing a
> single work of '245 solar street lights' against the price of *one* light — so of course it
> looked enormous.
>
> We found it, we parsed the quantity, and we compared **per-unit price**: ₹22,000 per light,
> entirely normal. Batch enrichment dropped from **4.03× to 1.15×**.
>
> We are showing you a bug we found in our own system and fixed, because that is what
> validation is for."

---

## 15. The five rules we refuse to break

**End the demo on this. It is what separates this from a hackathon toy.**

> "Five constraints we held all the way through:
>
> **1. No fraud verdicts.** The output is an *investigation lead* with evidence. There is an
> automated test that greps our entire source tree and **fails the build** if anyone
> introduces a variable named `fraud_score` or similar. It has caught us twice — including
> inside our own safety filter.
>
> **2. No fraud classifier.** There are no fraud labels, so any model claiming to predict
> fraud would be fabricated. Our scoring is transparent, weighted and rule-based, and you can
> read the weights.
>
> **3. Silhouette is not accuracy.** Ours is 0.050 and we say so everywhere.
>
> **4. ACTUAL_AMOUNT is not expenditure.** We measured it: 98.35% exact match. So we built no
> expenditure analysis rather than a fake one.
>
> **5. Human-in-the-loop.** Every single recommendation ends in 'a human should check X'.
>
> The impact is not *'AI detects corruption'*. The impact is giving public authorities a
> scalable, explainable way to decide **where evidence deserves human attention.**"

---

## 16. Likely questions, with short answers

| Question | Answer |
|---|---|
| **"Is this actually AI?"** | Three trained models — a sentence-transformer embedding, K-means clustering, a Cox survival model, an isolation forest — plus a language model for written briefings only. The LLM never computes a number. |
| **"Why not just train a fraud classifier?"** | There are no fraud labels in this data. Any such model would be fabricated. That is the honest core of our submission. |
| **"How accurate is it?"** | We refuse to quote a fraud accuracy, because there is nothing to measure it against. We quote synthetic detection (69.2%) and a survival C-index (0.6759), and we explain what each means. |
| **"What if it flags an innocent work?"** | It is designed to. It produces *leads*, not findings. Every lead carries its evidence and ends with a human action. Nobody is accused. |
| **"Can it scale nationally?"** | It already runs on the full national portfolio — 2.1 lakh works, four minutes, on a laptop, no GPU. |
| **"What is missing?"** | Payments, vendor details, cost estimates, GPS and photographs are not in the public data. The Data Transparency screen lists each one, and typed interfaces are already in place for when they arrive. |
| **"Why is the chatbot trustworthy?"** | It has ten read-only lookup tools and no arithmetic. Anything it says came from the deterministic pipeline, and it shows which tool it used. |
| **"Is it only in English?"** | Ten languages, statically translated so it never depends on a network call. |

---

## 17. If something breaks live

| Symptom | Fix |
|---|---|
| Every screen empty, numbers show `0` or `—` | The API is not running. Start Terminal 1. |
| `only one usage of each socket address` | A stale server holds port 8000. `taskkill /F /IM python.exe` |
| Red `UnauthorizedAccess` on `npm` | Use `npm.cmd run dev`, not `npm run dev` |
| Vite opened on 5175 instead of 5173 | Stale servers hold the lower ports. Harmless — just use the printed port. |
| Interface is in Tamil | Language switcher, top right → English. |
| A briefing panel looks plain | It fell back to a deterministic template. Say so — it is designed to degrade, and the panel labels itself. |

**Universal recovery line if anything misbehaves:**

> "That is the fallback path doing its job — the system is built so that when a component is
> unavailable it degrades honestly and says so, rather than showing you a number it cannot
> stand behind."

---

## The closing 20 seconds

> "Today an official cannot read two lakh works, so monitoring only happens after something
> has gone wrong.
>
> We give them a ranked list of where to look, with the reason attached, in their own
> language, and a record of what was found when somebody actually went.
>
> We never accuse anyone. We move oversight from **'what happened?'** to **'where should I
> look first?'** — and we were honest about everything this data cannot tell you."
