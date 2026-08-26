import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Topbar } from "../components/Bits.jsx";

const STEPS = [
  { n: 1, icon: "🧩", title: "Learn what normal looks like",
    plain: "There are over 2 lakh works — roads, halls, street lights, water tanks. The computer reads each work's description and groups similar ones together, so a road is compared with roads and a hall with halls, not with everything at once." },
  { n: 2, icon: "⚖️", title: "Compare each work with its true peers",
    plain: "For every work we find genuinely similar works in the same state and of the same type, then ask: is this one unusually expensive, or taking unusually long, compared to those peers? Being different from the national average is not enough — it must be different from its real peers." },
  { n: 3, icon: "🔮", title: "Predict which works may not finish",
    plain: "Many works are still ongoing. Using the history of how long similar works took to finish, the model estimates how likely each unfinished work is to stall. Money tied up in works that may not complete is 'exposure at risk'." },
  { n: 4, icon: "📈", title: "Notice when behaviour changes",
    plain: "For each implementing agency we watch how their pattern of works changes over the years. A sudden shift is worth a second look — though it can have an innocent reason, like a new officer or a rule change." },
  { n: 5, icon: "🗂️", title: "Explain and prioritise",
    plain: "We only raise a work when at least two independent kinds of evidence agree — never on a single hunch. Each raised work becomes a plain 'case file' listing exactly why, and the one thing a human should check next. The list is ranked so auditors look at the biggest money-at-risk first." },
];

function metricCard(m, title, plain) {
  if (!m) return null;
  return (
    <div className="card">
      <h3>{title}</h3>
      <div style={{ fontWeight: 640, marginBottom: 6 }}>{m.model}</div>
      <p className="muted" style={{ fontSize: 13, marginBottom: 10 }}>{plain}</p>
      <p style={{ fontSize: 12, color: "var(--text-2)" }}>{m.note}</p>
    </div>
  );
}

export default function HowItWorks() {
  const [m, setM] = useState(null);
  useEffect(() => { api.models().then(setM).catch(() => setM({})); }, []);

  const arch = m?.archetype_clustering;
  const risk = m?.completion_risk;
  const anom = m?.anomaly_detection;

  return (
    <>
      <Topbar title="How this works" sub="In plain English" />
      <div className="content">
        <div className="hitl">
          <span>💡</span>
          <span>
            This system is an <strong>assistant for auditors</strong>. It does not accuse
            anyone. It reads public records of government-funded local works and points to
            the ones most worth a human's time — always with the reason attached.
          </span>
        </div>

        <div className="card" style={{ marginBottom: 22 }}>
          <h3>What problem does it solve?</h3>
          <p style={{ fontSize: 14, color: "var(--text)" }}>
            Members of Parliament recommend local development works — roads, community halls,
            street lights, water supply. There are over <strong>2,10,000</strong> of them
            across the country. No official can check them all by hand. This system reads
            every work and produces a short, ranked list of the ones that look unusual
            compared to genuinely similar works — so limited audit time goes where it matters
            most. Every item is an <strong>investigation lead, not a verdict</strong>.
          </p>
        </div>

        <div className="section-title">The five steps</div>
        {STEPS.map((s) => (
          <div className="card" key={s.n} style={{ marginBottom: 12, display: "flex", gap: 16 }}>
            <div className="evidence-icon" style={{ width: 40, height: 40, fontSize: 20, flexShrink: 0 }}>{s.icon}</div>
            <div>
              <div style={{ fontWeight: 660, fontSize: 15 }}>
                <span className="muted" style={{ marginRight: 8 }}>Step {s.n}</span>{s.title}
              </div>
              <p className="muted" style={{ fontSize: 13.5, marginTop: 4 }}>{s.plain}</p>
            </div>
          </div>
        ))}

        <div className="section-title">The models we trained — and how honest they are</div>
        <div className="grid cols-3">
          {metricCard(arch,
            arch ? `Grouping works · ${arch.k_chosen} archetypes` : "Grouping works",
            "The computer turns each description into numbers and groups similar ones. We tried several group counts and kept the clearest.")}
          {metricCard(risk,
            risk ? `Completion risk · accuracy ${Math.round((risk.c_index_heldout) * 100)}%` : "Completion risk",
            "A survival model, the same maths used to study how long things last, that respects the fact many works are still ongoing rather than failed.")}
          {metricCard(anom,
            anom ? `Outlier detector · ${anom.n_flagged?.toLocaleString("en-IN")} flagged` : "Outlier detector",
            "A model that learns the normal amount-and-age profile and flags the statistical odd-ones-out as one extra piece of evidence.")}
        </div>

        <div className="card" style={{ marginTop: 20 }}>
          <h3>What we are careful NOT to claim</h3>
          <ul style={{ fontSize: 13.5, color: "var(--text-2)", paddingLeft: 18, lineHeight: 1.9 }}>
            <li>We do <strong>not</strong> call anything fraud. There are no fraud records in this data to learn from, so any "fraud detector" would be made up.</li>
            <li>The "grouping quality" score (silhouette ≈ 0.05) is a <strong>separation measure, not accuracy</strong>. We say so plainly.</li>
            <li>"Exposure at risk" is money that <strong>could</strong> be tied up in works that may not finish — it is not proven loss or missing money.</li>
            <li>Every case ends with <strong>"a human should check…"</strong>. People decide; the computer only points.</li>
          </ul>
        </div>
      </div>
    </>
  );
}
