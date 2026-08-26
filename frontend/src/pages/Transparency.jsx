import { useEffect, useState } from "react";
import { api, num } from "../api.js";
import { Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";

const TYPE = {
  "Direct measurement": { c: "#2f5d3f", t: "Measured" },
  "Model-derived": { c: "#a8452a", t: "Derived" },
  Unavailable: { c: "#a8452a", t: "Unavailable" },
};

export default function Transparency() {
  const [d, setD] = useState(null);
  useEffect(() => { api.transparency().then(setD).catch(console.error); }, []);

  if (!d) return (<><Topbar title="Data Transparency" /><div className="content"><Loading /></div></>);

  const group = (type) => d.metrics.filter((m) => m.type === type);

  return (
    <>
      <Topbar title="Data Transparency"
        sub="What we measure, what we derive, and what the public data does not contain"
        right={<span className="pill">{d.totals.unavailable_metrics} fields unavailable</span>} />
      <div className="content">
        <div className="hitl">
          <span>🔒</span>
          <span><strong>{d.statement}</strong></span>
        </div>

        <Reveal><div className="grid cols-3">
          <div className="card stat">
            <div className="label">Measured directly</div>
            <div className="value" style={{ fontSize: 28, color: "#2f5d3f" }}>{d.totals.available_metrics}</div>
            <div className="foot">straight from government records</div>
          </div>
          <div className="card stat">
            <div className="label">Model-derived</div>
            <div className="value" style={{ fontSize: 28, color: "#a8452a" }}>{d.totals.derived_metrics}</div>
            <div className="foot">computed, with stated confidence</div>
          </div>
          <div className="card stat">
            <div className="label">Unavailable</div>
            <div className="value" style={{ fontSize: 28, color: "#a8452a" }}>{d.totals.unavailable_metrics}</div>
            <div className="foot">absent from public data — not faked</div>
          </div>
        </div>

        </Reveal>
        {["Direct measurement", "Model-derived", "Unavailable"].map((type) => (
          <div key={type}>
            <div className="section-title">{TYPE[type].t}</div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Metric</th><th>Source</th><th>Confidence</th><th>Note</th></tr></thead>
                <tbody>
                  {group(type).map((m) => (
                    <tr key={m.metric}>
                      <td style={{ fontWeight: 600 }}>{m.metric}</td>
                      <td className="muted" style={{ fontSize: 12 }}>{m.source}</td>
                      <td><span className="badge" style={{ color: TYPE[type].c, background: "#f1ece1" }}>{m.confidence}</span></td>
                      <td className="muted" style={{ fontSize: 12 }}>{m.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}

        <div className="section-title">Field completeness (measured)</div>
        <div className="card">
          {d.completeness.map((f) => (
            <div key={f.field} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                <span>{f.field}</span><span>{f.present_pct}%</span>
              </div>
              <div className="meter">
                <span style={{ width: `${f.present_pct}%`, background: f.present_pct > 95 ? "#2f5d3f" : "#9a6b1f" }} />
              </div>
            </div>
          ))}
        </div>

        <div className="section-title">Ready for restricted government data</div>
        <div className="card">
          <p className="muted" style={{ fontSize: 13, marginBottom: 14 }}>
            The ingestion schema already carries typed, optional interfaces for the fields a
            MoSPI data grant would unlock. They are null today; nothing needs restructuring
            when they arrive.
          </p>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Field</th><th>Type</th><th>What it would unlock</th></tr></thead>
              <tbody>
                {d.future_fields.map((f) => (
                  <tr key={f.field}>
                    <td style={{ fontFamily: "monospace", fontSize: 12 }}>{f.field}</td>
                    <td className="muted" style={{ fontSize: 12 }}>{f.dtype}</td>
                    <td>{f.unlocks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
