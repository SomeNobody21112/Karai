import { useEffect, useState } from "react";
import { api, num } from "../api.js";
import { Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";
import { scoreFill, sev } from "../severity.js";

/**
 * How far a number is from the raw record. Measured straight from government data
 * is the reassuring case, absent-from-the-data the one a reader must not miss —
 * so it rides the same ladder as everything else. "Derived" and "Unavailable" were
 * previously the same terracotta, which flattened the honest distinction this
 * whole screen exists to draw.
 */
const TYPE = {
  "Direct measurement": { level: "LOW", t: "Measured" },
  "Model-derived": { level: "MEDIUM", t: "Derived" },
  Unavailable: { level: "HIGH", t: "Unavailable" },
};

/**
 * How much weight a figure can carry. The badge shows the confidence word, so it
 * is coloured by the confidence — not by the section it sits under, which would
 * put a reassuring green marker next to the word "High" inside the Unavailable
 * table and read as the opposite of what it means.
 */
const CONFIDENCE = { High: "LOW", Medium: "MEDIUM", Low: "HIGH", None: "HIGH" };

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
            <div className="value" style={{ fontSize: 28, color: sev("LOW").ink }}>{d.totals.available_metrics}</div>
            <div className="foot">straight from government records</div>
          </div>
          <div className="card stat">
            <div className="label">Model-derived</div>
            <div className="value" style={{ fontSize: 28, color: sev("MEDIUM").ink }}>{d.totals.derived_metrics}</div>
            <div className="foot">computed, with stated confidence</div>
          </div>
          <div className="card stat">
            <div className="label">Unavailable</div>
            <div className="value" style={{ fontSize: 28, color: sev("HIGH").ink }}>{d.totals.unavailable_metrics}</div>
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
                      <td>
                        <span className="badge sev" title={`Confidence: ${m.confidence}`} style={{
                          color: sev(CONFIDENCE[m.confidence]).ink,
                          background: sev(CONFIDENCE[m.confidence]).soft,
                        }}>
                          <i className="glyph" aria-hidden="true">{sev(CONFIDENCE[m.confidence]).glyph}</i>
                          {m.confidence}
                        </span>
                      </td>
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
                <span style={{ width: `${f.present_pct}%`, background: scoreFill(f.present_pct / 100) }} />
              </div>
            </div>
          ))}
        </div>

        <div className="section-title">Ground truth from the field</div>
        <GroundTruth />

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

/**
 * The one honest answer to "how accurate is it?".
 *
 * Nothing in the source data says which works were actually problems, so no score on
 * this site has ever been checked against an outcome. Officers recording what they
 * found on site are the only way that ever changes — and this counts how far off it
 * still is, rather than implying it has already happened.
 */
function GroundTruth() {
  const [d, setD] = useState(null);
  useEffect(() => { api.fieldSummary().then(setD).catch(() => setD({ error: true })); }, []);

  if (!d) return <div className="card"><Loading /></div>;
  if (d.error) return null;

  const r = d.readiness;
  const target = r.verifications + r.labels_needed_to_fit_weights;
  const pct = target ? (r.verifications / target) * 100 : 0;

  return (
    <div className="card">
      <p className="muted" style={{ fontSize: 13, marginBottom: 16 }}>
        No dataset anywhere records which MPLADS works turned out to be problems, so every
        weight on this site is a reasoned default, not a fitted one. A verification is an
        officer writing down what they found when they went and looked — the only ground
        truth this system can ever obtain, one site visit at a time.
      </p>

      <div className="grid cols-3" style={{ marginBottom: 16 }}>
        <div className="card stat">
          <div className="label">Verifications recorded</div>
          <div className="value" style={{ fontSize: 28 }}>{num(r.verifications)}</div>
          <div className="foot">across {num(r.works_verified)} works</div>
        </div>
        <div className="card stat">
          <div className="label">Concerns confirmed on site</div>
          <div className="value" style={{ fontSize: 28,
            color: r.concerns_confirmed > 0 ? sev("HIGH").ink : undefined }}>
            {num(r.concerns_confirmed)}
          </div>
          <div className="foot">not started, not found or mismatched</div>
        </div>
        <div className="card stat">
          <div className="label">Still needed to fit weights</div>
          <div className="value" style={{ fontSize: 28 }}>{num(r.labels_needed_to_fit_weights)}</div>
          <div className="foot">threshold is {num(target)} records</div>
        </div>
      </div>

      <div className="meter" style={{ marginBottom: 14 }}>
        <span style={{ width: `${Math.max(pct, 0.5)}%`, background: scoreFill(pct / 100) }} />
      </div>

      {Object.keys(r.by_outcome).length > 0 && (
        <div className="table-wrap" style={{ marginBottom: 14 }}>
          <table>
            <thead><tr><th>Outcome</th><th>Meaning</th><th style={{ textAlign: "right" }}>Records</th></tr></thead>
            <tbody>
              {Object.entries(r.by_outcome).map(([k, n]) => (
                <tr key={k}>
                  <td style={{ fontWeight: 600 }}>{k.replace(/_/g, " ")}</td>
                  <td className="muted" style={{ fontSize: 12 }}>{d.outcomes[k]}</td>
                  <td style={{ textAlign: "right", fontFamily: "monospace" }}>{num(n)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="muted" style={{ fontSize: 12.5, lineHeight: 1.7 }}>
        {r.note} Records are immutable and attributed to the officer who made them; a
        correction is a new record, never an edit.
        {d.ocr_available
          ? " Photographs of site boards are read automatically so nobody re-types a reference number standing in a field."
          : " Photo reading is unavailable on this machine, so references are entered by hand."}
      </p>
    </div>
  );
}
