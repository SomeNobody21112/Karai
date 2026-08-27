# Our Models, In Very Simple English

**A script you can read out loud.** No maths. No jargon without a plain meaning right next to it.

Read this if you have to explain the technical side to anyone — a judge, a teacher, a friend,
your parents.

---

## First, the one-line answer

> "We built a system that reads 2,10,993 real government works, learns what normal looks
> like, and then points out the ones worth a closer look — with the reason attached."

If someone asks nothing else, that sentence is enough.

---

## The big idea (say this first, always)

Imagine you are a school teacher with **2,10,993 answer sheets**.

You cannot read them all. Nobody can.

So what do you do? You do three things:

1. You **group** the sheets by question type. Maths with maths. Essays with essays.
2. Inside each group, you notice the ones that **look different** from the rest.
3. You give those few sheets to a human to actually read.

That is our whole system. Nothing more clever than that.

**We never say "this student cheated."** We say "this sheet looks different from the others,
here is why, please have a look."

That last line is the most important sentence in the whole project.

---

## Why we cannot just build a "fraud detector"

This is the question judges ask first. Here is the honest answer.

To teach a computer to spot fraud, you need **examples of fraud**. You need thousands of old
records where someone has already written "this one was fraud" and "this one was fine."

**No such list exists.** Not in this data. Not anywhere public.

So if any team shows you a screen saying *"Fraud probability: 87%"* — that number is made up.
It cannot be anything else. There was nothing to learn from.

We refused to fake it. Instead we built something we *can* honestly do: find the unusual ones
and explain why they are unusual. That is a **lead**, not a verdict.

> **Say it like this:** "A fraud score needs examples of fraud to learn from. There are none.
> So we don't give you a fraud score. We give you evidence and let a human decide."

---

## The three models we actually trained

We trained exactly three. Here they are.

---

### Model 1 — The Sorter (finding "kinds of work")

**What problem does it solve?**

Every work has a written description. Things like:

- *"Construction of community hall at village X"*
- *"Building of community centre, ward 4"*
- *"Community hall construction work"*

A human reads those three and instantly knows: **same kind of thing.**

A computer sees three completely different strings of letters.

**What we did**

We used a ready-made language model called **MiniLM**. Think of it as a translator that turns
a sentence into a list of numbers. Sentences that *mean* the same thing get *similar* numbers.

Then we used a method called **K-Means clustering**. In plain words: throw all the number-lists
onto a table and let similar ones fall into piles.

**The result: 50 piles.** We call them **archetypes** — a fancy word for "kinds of work."

Roads in one pile. Solar street lights in another. Community halls in another.

**Nobody told it these categories.** It found them on its own by reading 1,87,865 descriptions.

**Why this matters so much**

Because now we can compare fairly.

A ₹42 lakh community hall does not look strange next to a ₹40 crore highway. But next to
*other community halls in the same state*, it might look very strange indeed.

**You cannot spot an odd one out until you know what it should be compared to.** This model
gives us that.

**The honest part — say this before a judge finds it**

We measure how clean the piles are with a score called **silhouette**. Ours is **0.050**.

That is a low number. It means the piles overlap a lot at the edges. Work descriptions in real
government data are messy — half of them are pasted-in tables and spelling mistakes.

**Silhouette is not accuracy.** It does not mean "5% correct." It measures separation, not
correctness. We say this in our code, our documents and on the website itself.

We named 49 of the 50 piles. One pile we could not understand, so we labelled it
**"uninterpretable"** and left it that way. Saying "we don't know" is better than inventing a
name.

---

### Model 2 — The Predictor (which works may not finish)

**What problem does it solve?**

Everyone wants to know: *how late are MPLADS works?*

The obvious way is to look at finished works and count the days. **That answer is wrong.** Badly
wrong.

Here is why, and this is the best story in our whole project:

> Imagine measuring how long people stay in hospital — but you only survey people who have
> **already gone home**.
>
> You will get a lovely small number. Because the people still lying in bed, the ones who have
> been there for months, are not in your survey at all.
>
> **The worst cases are invisible, exactly because they are the worst.**

Our data has **85,773 finished** works and **1,25,220 still open**. If we only measure the
finished ones, we throw away the bigger half — and it is the *worse* half.

This mistake has a name: **survivorship bias**.

**What we did**

We used **survival analysis** — the same maths hospitals and insurance companies use. It was
invented for exactly this problem.

The trick is a word called **censoring**. For a work that is still open, we don't pretend we
know how long it took. We tell the model something weaker but true:

> *"This one has been running 400 days and has not finished yet. Whatever the true answer is,
> it is **more than 400 days**."*

That is still useful information. The old method threw it in the bin.

The specific model is called **Cox proportional hazards**. It looks at the type of work, the
amount, the state, and the agency, and estimates the chance a work finishes in a given time.

**How good is it?**

We measure it with the **C-index**. This asks a simple question:

> *Take any two works. Did the model correctly guess which one finishes first?*

- **0.5** = coin flip, useless
- **1.0** = perfect, never happens in real life
- **Ours: 0.6759**

So: **right about 68 times out of 100**, on works it had never seen.

That is honestly a modest score. It is also a real one, measured on held-out data. It is much
better than a coin flip, and far better than the biased number everybody else quotes.

**What we do with it**

We multiply the risk by the money.

> Risk of not finishing **×** amount recommended **=** **₹ exposure**

Across the country this comes to **₹1,302 crore**.

**Say this exact sentence:** *"₹1,302 crore sits in works our model thinks may not finish on
time. That is money to watch. It is **not** money lost, not money stolen, not money missing."*

Officials act on rupees. They do not act on "risk = 0.83". This is the model's real output.

---

### Model 3 — The Second Opinion (Isolation Forest)

**What problem does it solve?**

Model 1 and 2 look at things we chose to look at — amount, duration, type. What if something is
strange in a way we never thought to check?

**What we did**

We used **Isolation Forest**. The name explains it, which is rare.

It plays a game: *how quickly can I separate this one work from all the others by asking random
yes/no questions?*

An ordinary work hides in the crowd. You need many questions to isolate it.

An odd work gets separated in two or three questions. **Easy to isolate = unusual.**

It flagged **4,220 works**.

**Why we keep it small**

This model is only a **cross-check**. It never raises an alarm by itself.

Its job is to agree or disagree with the others. If the amount looks odd *and* the duration
looks odd *and* this model also says odd — three different methods agreeing is much stronger
than any one of them shouting.

---

## The other engines (not trained models — but important)

These are not machine learning. They are careful statistics and rules. **We never call rules
"AI".** Being precise about this earns trust.

### Peer comparison

For each work we find its true peers — same kind of work, same state, similar size — and ask
where it sits among them.

If a group has fewer than 30 peers, we **back off** to a wider group rather than compare against
five works and pretend that means something.

One important detail: a work is **never compared against itself**. It sounds obvious. It is easy
to get wrong, and it quietly inflates every result if you do.

### Duplicate detection

We look for works with nearly identical descriptions.

We found **2,23,407 similar pairs**. If we had shouted about all of them we would have been
laughed at — government works are *supposed* to repeat. Every district builds solar lights.

So we narrowed it: **same agency + nearly the same amount + nearly the same words**. That leaves
**47,709 worth a look** — and even those are questions, not accusations.

### Lifecycle and compliance checks

Simple, checkable rules. Did a work get marked complete before it was recommended? Is a stage
missing? Is a date impossible?

**5,946 works** trip at least one check.

Every check says what kind of rule it is. **None of them claims to be an official government
rule** — we do not have the rulebook, so we never pretend a statistical oddity is a legal
breach. That would be inventing law.

### Behaviour over time

Instead of looking at one work, we look at one **agency** across years.

A hundred works can each look completely normal while the agency that produced them quietly
changes — bigger amounts, different kinds of work, fewer completions.

**No single work can show you that.** The change is not in any one row.

Right now **73 of 697 agencies** show a measurable shift in behaviour.

**A change is never a bad thing by itself.** A new officer, a new state scheme, or a flood all
look exactly the same in the data. We show the before and after side by side and let a human
explain it.

### Evidence fusion

Now we combine everything.

We group the signals into **families** — amount, duration, lifecycle, behaviour, statistical
outlier, duplication. Then we count **how many independent families agree** on the same work.

- **1 family** agreeing → usually just noise
- **2 families** → worth a look — *MEDIUM*
- **3 or more** → **HIGH** confidence

Out of 2,10,993 works, **37,705** were surfaced. Of those, **4,478 are HIGH**.

The reason we count *families* and not *signals*: two signals that come from the same source are
not two pieces of evidence. They are one piece of evidence counted twice.

### Ranking who to check first

An auditor has limited days. So we rank by:

> how unusual it is **×** how much money **×** how many families agree

We call it **Audit-ROI**. It answers: *where is one day of an auditor's time worth most?*

It is a **queue order, never a measure of guilt.**

---

## Do we know if any of this works?

Fair question. Here is the honest answer, in two halves.

### What we can prove

We ran a test. We took the real data and **deliberately damaged some of it** — we planted
problems we created ourselves, so we knew exactly where they were. Then we asked the system to
find them without telling it.

| What we planted | How much we caught |
|---|---|
| Works that stalled | **96.1%** |
| Inflated amounts | **83.2%** |
| Broken lifecycles | **58.0%** |
| Copied works | **50.0%** |
| **Overall** | **69.2%** |

This proves the machinery works. **It does not prove anything about real fraud** — we planted
those problems ourselves. We label every one of these numbers as synthetic, every time.

### What we cannot prove

**Nothing here has ever been checked against a real outcome.** Because there is no list of real
outcomes.

So we built the only thing that can ever fix that: a screen where an officer records **what they
actually found when they went and looked**.

An officer photographs the work board at the site. The system reads it, matches it to the work,
and checks whether that same photograph has been submitted before for a different work.

Those records are the missing answer key — collecting one site visit at a time. When there are
about 500, our numbers stop being reasoned guesses and start being fitted to what officers
really found.

We are nowhere near 500. **Our website shows the real count and how far away it is** — rather
than quietly implying we are done.

---

## Three things we tested and threw away

This is our favourite part. A team that says *"we tried it and it failed"* is more trustworthy
than one where everything worked.

**1. Amounts just below approval limits.** The classic fraud signal. We tested it. Amounts
cluster at **round numbers** — ₹5 lakh, ₹10 lakh — because that is how budgets are written, not
because anyone is dodging a limit. Killed it.

**2. Agencies with too many works.** Sounds suspicious. It is not. The "agency" is the District
Collector's office. Of course it has all the works — that is its job. It is administration, not
wrongdoing. Killed it.

**3. Cost overruns.** We wanted this badly. Then we measured: the "actual amount" field equals
the recommended amount **exactly, on 98.35% of finished works**. It is a completion tick-box,
not a record of spending. There is no overrun signal in this data. Anyone claiming one is making
it up. Killed it.

---

## If they ask a hard question

**"Isn't this just an Excel GROUP BY?"**
> No. A GROUP BY cannot handle unfinished works without throwing them away. It cannot find when
> an agency changed. It cannot rank under a budget. Those are the three things we built.

**"How accurate is it?"**
> On planted test problems, 69.2%. On real fraud, we don't know and nobody can — there is no
> answer key. We would rather tell you that than show you a number we invented.

**"Why 50 groups?"**
> We tried 20, 30, 40, 50 and 60 and measured each one. 50 scored best. It is not a number we
> liked the look of.

**"So the AI decides who gets audited?"**
> No. It puts names in an order and shows the reason for each. A human decides. Every single
> screen says so.

**"What if you accuse an innocent district?"**
> We never accuse anyone. There is no accusation anywhere in this system — only "here is
> something unusual, here is why, please check." And we show the evidence so a person can
> disagree with us in thirty seconds.

---

## The closing line

> "Other teams will tell you how late the finished works were.
>
> That number is a lie — it quietly ignores every work that never finished at all.
>
> We don't. And we won't tell you anything is fraud, because we cannot know that.
>
> We tell you where to look first, why, and how much money is sitting there."

---

## Numbers to memorise

| | |
|---|---|
| Works | **2,10,993** |
| Raw lifecycle rows | **4,80,768** |
| Finished / still open | **85,773 / 1,25,220** |
| Total recommended | **₹11,565 crore** |
| Money to watch (exposure) | **₹1,302 crore** |
| Surfaced for review | **37,705** (**4,478** HIGH) |
| States / constituencies / agencies | **36 / 545 / 778** |
| Kinds of work learned | **50** (silhouette **0.050** — separation, not accuracy) |
| Prediction score | **C-index 0.6759** |
| Second-opinion flags | **4,220** |
| Planted-problem detection | **69.2%** (synthetic) |
| Automatic tests passing | **189** |

**Never estimate these. Quote them exactly, or don't quote them.**
