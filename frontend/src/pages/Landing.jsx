import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, rupees } from "../api.js";
import { useScrollY } from "../hooks.js";
import { CountUp, Reveal } from "../components/Reveal.jsx";

const STEPS = [
  {
    n: "01",
    title: "Learn what normal looks like",
    body: "The system reads the description of every single work and sorts them into groups of similar things — roads with roads, community halls with halls, street lights with street lights. It discovered 50 such work types entirely on its own.",
    analogy: "Like tipping out a giant box of mixed Lego and sorting it into piles — wheels, flat pieces, roof pieces — without anyone telling you those piles exist.",
  },
  {
    n: "02",
    title: "Compare each work with its true peers",
    body: "For every work we find works of the same type in the same state, then ask: compared to those, is this one unusually expensive, or taking unusually long? Being different from the national average is not enough.",
    analogy: "To know if you overpaid for a school bag, you compare it to other school bags in your town — not to every object in the shop.",
  },
  {
    n: "03",
    title: "Predict which works may stall",
    body: "Most works are still in progress, and that is normal. Using the history of how long similar works took, a trained survival model estimates which unfinished works are unlikely to complete — without ever calling an in-progress work a failure.",
    analogy: "Watching a marathon: from how long finishers took and how far each runner has gone, you can sensibly say who probably won't finish.",
  },
  {
    n: "04",
    title: "Notice when behaviour changes",
    body: "For each implementing office we watch its pattern year by year. An office that always handled small works and suddenly handles very large ones has changed — and that is worth a second look, even though the reason is often innocent.",
    analogy: "A shop that sold ₹100 a day for two years suddenly sells ₹5,000 a day. Maybe a new road brought customers. You would at least ask.",
  },
  {
    n: "05",
    title: "Explain, then prioritise",
    body: "Clues are combined — but a work is only raised when at least two independent kinds of evidence agree. Each becomes a case file listing exactly why, plus the one thing a human should check next, ranked so the biggest money-at-risk comes first.",
    analogy: "In a courtroom, one witness isn't enough. You want two who never spoke to each other before you take a claim seriously.",
  },
];

const FEATURES = [
  { ic: "🧠", h: "Semantic understanding", p: "Every description becomes a 384-number fingerprint, so the system knows 'CC Road' and 'construction of concrete road' mean the same thing." },
  { ic: "⧉", h: "Near-duplicate detection", p: "Finds works claimed twice by meaning, not by text matching — then narrows to the pairs whose administrative pattern is genuinely odd." },
  { ic: "📈", h: "Temporal intelligence", p: "Labels every trend as normal, emerging, a sudden change or a persistent shift — using only recommendation-time data, so recency can't fake a signal." },
  { ic: "⚖️", h: "Compliance engine", p: "Eight lifecycle checks, each declaring whether it is an official rule, an observed baseline, or merely a statistical outlier." },
  { ic: "🔔", h: "Early warning", p: "Four risk levels for stalling works, and every single one shows the sentence that produced it. No bare scores anywhere." },
  { ic: "🔒", h: "Radical transparency", p: "A dedicated screen showing what we measure, what we derive, and exactly which government fields do not exist — proven with measurements." },
];

function Nav({ stuck }) {
  return (
    <nav className={"landing-nav" + (stuck ? " stuck" : "")}>
      <div className="brand" style={{ padding: 0 }}>
        <div className="brand-mark">M</div>
        <div>
          <div className="brand-name">MPLADS Intel</div>
          <div className="brand-sub">Forensic Monitoring</div>
        </div>
      </div>
      <Link to="/overview" className="btn btn-primary">
        Open the dashboard →
      </Link>
    </nav>
  );
}

export default function Landing() {
  const [stats, setStats] = useState(null);
  const y = useScrollY();

  useEffect(() => {
    api.stats().then(setStats).catch(() => {});
  }, []);

  const n = stats?.national;

  return (
    <div className="landing">
      <Nav stuck={y > 40} />

      {/* ---------------------------------------------------------- hero */}
      <header className="hero">
        <div className="hero-geo"><i /><i /><i /></div>
        <div className="hero-grid" />
        <div className="hero-inner">
          <div className="eyebrow">
            <span className="dot-live" />
            Smart India Hackathon 2026 · SIH26102 · MoSPI
          </div>
          <h1>
            Two lakh public works.<br />
            <span className="grad">One afternoon to check them.</span>
          </h1>
          <p className="lede">
            An AI monitoring layer over India's MPLADS scheme that reads every work,
            compares each against genuinely similar ones, and hands officials a short,
            ranked list of what deserves their attention — with the reason attached to
            every single item.
          </p>
          <div className="hero-cta">
            <Link to="/overview" className="btn btn-primary">Explore the dashboard</Link>
            <Link to="/how" className="btn">How it works</Link>
          </div>

          <div className="hero-stats">
            <div className="hero-stat">
              <div className="v">
                {n ? <CountUp end={n.total_works} /> : "—"}
              </div>
              <div className="l">Works analysed</div>
            </div>
            <div className="hero-stat">
              <div className="v" style={{ color: "var(--brass)" }}>
                {n ? <CountUp end={n.total_recommended_rupees / 1e7} decimals={0}
                  format={(v) => `₹${v.toLocaleString("en-IN")} Cr`} /> : "—"}
              </div>
              <div className="l">Recommended value</div>
            </div>
            <div className="hero-stat">
              <div className="v" style={{ color: "var(--high)" }}>
                {n ? <CountUp end={n.bands?.HIGH || 0} /> : "—"}
              </div>
              <div className="l">High-confidence leads</div>
            </div>
            <div className="hero-stat">
              <div className="v">50</div>
              <div className="l">Work types discovered</div>
            </div>
          </div>
        </div>
        <div className="scroll-hint">
          <span>Scroll</span>
          <span className="line" />
        </div>
      </header>

      {/* ------------------------------------------------------- problem */}
      <section className="section">
        <div className="section-inner">
          <Reveal><div className="kicker">The problem</div></Reveal>
          <Reveal delay={60}>
            <h2>Nobody can read two lakh notebooks.</h2>
          </Reveal>
          <Reveal delay={120}>
            <p className="sub">
              Members of Parliament recommend local works — roads, halls, street lights,
              water tanks. There are {n ? n.total_works.toLocaleString("en-IN") : "210,993"} of
              them, worth {n ? rupees(n.total_recommended_rupees) : "₹11,565 Cr"}. If an
              official spent one minute on each, doing nothing else all day, it would take
              them over a year to look at every work once.
            </p>
          </Reveal>

          <div className="feature-grid" style={{ marginTop: 40 }}>
            {[
              { v: "1 min", l: "per work", d: "barely enough to read the description" },
              { v: "17 months", l: "to review all of them once", d: "full-time, nothing else" },
              { v: "Reactive", l: "how monitoring works today", d: "you look after something goes wrong" },
            ].map((x, i) => (
              <Reveal key={x.l} delay={i * 90}>
                <div className="feature">
                  <div className="v" style={{
                    fontFamily: "Sora, sans-serif", fontSize: 30, fontWeight: 800,
                    letterSpacing: "-1px", marginBottom: 6,
                  }}>{x.v}</div>
                  <h4 style={{ marginBottom: 6 }}>{x.l}</h4>
                  <p>{x.d}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* --------------------------------------------------------- steps */}
      <section className="section alt">
        <div className="section-inner">
          <Reveal><div className="kicker">How it works</div></Reveal>
          <Reveal delay={60}><h2>Learn → Compare → Predict → Explain → Prioritise</h2></Reveal>
          <Reveal delay={120}>
            <p className="sub">Five steps. Every one of them explainable to a person who has
              never seen a line of code.</p>
          </Reveal>

          <div style={{ marginTop: 34 }}>
            {STEPS.map((s, i) => (
              <Reveal key={s.n} delay={i * 40}>
                <div className="step-row">
                  <div className="step-num">{s.n}</div>
                  <div>
                    <h3>{s.title}</h3>
                    <p>{s.body}</p>
                    <div className="analogy">{s.analogy}</div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------ features */}
      <section className="section">
        <div className="section-inner">
          <Reveal><div className="kicker">What is inside</div></Reveal>
          <Reveal delay={60}><h2>Seven engines, one explainable answer</h2></Reveal>
          <Reveal delay={120}>
            <p className="sub">
              Three trained models and four analytical engines feed a single transparent
              scoring layer. No black box anywhere in the chain.
            </p>
          </Reveal>
          <div className="feature-grid">
            {FEATURES.map((f, i) => (
              <Reveal key={f.h} delay={(i % 3) * 90} variant="scale">
                <div className="feature">
                  <div className="ic">{f.ic}</div>
                  <h4>{f.h}</h4>
                  <p>{f.p}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------- honesty */}
      <section className="section alt">
        <div className="section-inner">
          <Reveal><div className="kicker">The part that matters</div></Reveal>
          <Reveal delay={60}><h2>What we refuse to claim</h2></Reveal>
          <Reveal delay={120}>
            <p className="sub" style={{ marginBottom: 30 }}>
              There are no fraud labels in any public MPLADS source. Any system claiming a
              fraud-detection accuracy on this data has invented it. We built the honest
              version instead.
            </p>
          </Reveal>
          <Reveal variant="scale">
            <div className="honesty-card">
              <ul className="honesty-list">
                <li><span className="x">✕</span><span><b>We never say "this work is fraudulent."</b> We say "a human should check this, and here is why."</span></li>
                <li><span className="x">✕</span><span><b>We never quote a fraud accuracy.</b> Accuracy against what? There is no answer key.</span></li>
                <li><span className="x">✕</span><span><b>We never call exposure "lost money."</b> It is money tied up in works that may not finish.</span></li>
                <li><span className="x">✕</span><span><b>We never claim cost-overrun detection.</b> No cost estimate exists anywhere in the data.</span></li>
                <li><span className="tick">✓</span><span><b>We do prove the machinery works.</b> We plant known anomalies into real records and measure how many the system catches — 96% of stalled works, 83% of inflated amounts.</span></li>
                <li><span className="tick">✓</span><span><b>We do publish our weak numbers.</b> Cluster separation is 0.05 and we say so, loudly, because it is a separation measure and never an accuracy.</span></li>
              </ul>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ---------------------------------------------------------- CTA */}
      <section className="section">
        <div className="section-inner" style={{ textAlign: "center" }}>
          <Reveal>
            <h2 style={{ maxWidth: 760, margin: "0 auto 18px" }}>
              From <span style={{ color: "var(--text-3)" }}>"what happened?"</span> to{" "}
              <span className="grad">"where should I look first?"</span>
            </h2>
          </Reveal>
          <Reveal delay={90}>
            <p className="sub" style={{ margin: "0 auto 32px" }}>
              {n ? `${n.bands?.HIGH?.toLocaleString("en-IN")} high-confidence leads` : "Leads"} out
              of {n ? n.total_works.toLocaleString("en-IN") : "210,993"} works — each one with
              its evidence, its peer context, and one recommended human action.
            </p>
          </Reveal>
          <Reveal delay={160}>
            <Link to="/overview" className="btn btn-primary" style={{ padding: "14px 30px", fontSize: 14.5 }}>
              Open the dashboard →
            </Link>
          </Reveal>
        </div>
      </section>

      <footer className="landing-foot">
        <b style={{ color: "var(--text-2)" }}>Team Morior Invictus</b> · Smart India Hackathon 2026<br />
        Problem Statement SIH26102 · Ministry of Statistics and Programme Implementation<br />
        <span style={{ opacity: 0.7 }}>
          Investigation leads, not fraud verdicts. A human decides every action.
        </span>
      </footer>
    </div>
  );
}
