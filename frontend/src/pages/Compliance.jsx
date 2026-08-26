import { useEffect, useState } from "react";
import { api, num, rupees } from "../api.js";
import { Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";

const AUTHORITY = {
  OFFICIAL_RULE: { c: "#ff5f7a", t: "Official rule" },
  OBSERVED_BASELINE: { c: "#ffb340", t: "Observed baseline" },
  STATISTICAL_OUTLIER: { c: "#6c8cff", t: "Statistical outlier" },
};
const SEV = { HIGH: "#ff5f7a", MEDIUM: "#ffb340", LOW: "#6c8cff" };

export default function Compliance() {
  const [c, setC] = useState(null);
  const [w, setW] = useState(null);
  const [h, setH] = useState(null);

  useEffect(() => {
    api.compliance().then(setC).catch(console.error);
    api.earlyWarning().then(setW).catch(() => {});
    api.healthIndex().then(setH).catch(() => {});
  }, []);

  if (!c || !w || !h) return (<><Topbar title="Compliance & Early Warning" /><div className="content"><Loading /></div></>);

  return (
    <>
      <Topbar title="Compliance & Early Warning"
        sub="Lifecycle deviation checks and stalling risk"
        right={<span className="pill">Health Index {h.score}/100</span>} />
      <div className="content">
        <div className="hitl">
          <span>⚖️</span>
          <span><strong>Authority matters.</strong> {c.authority_note}</span>
        </div>

        <div className="section-title">MPLADS Operational Health Index — {h.score}/100</div>
        <div className="card" style={{ marginBottom: 20 }}>
          {h.components.map((comp) => (
            <div key={comp.name} style={{ marginBottom: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                <span style={{ fontWeight: 600 }}>
                  {comp.name} <span className="muted">· weight {(comp.weight * 100).toFixed(0)}%</span>
                </span>
                <span>{(comp.value * 100).toFixed(1)}%</span>
              </div>
              <div className="meter"><span style={{ width: `${comp.value * 100}%`, background: "#6c8cff" }} /></div>
              <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>{comp.explanation}</div>
            </div>
          ))}
          <div className="muted" style={{ fontSize: 12, borderTop: "1px solid var(--line-soft)", paddingTop: 10 }}>
            {h.note}
          </div>
        </div>

        <Reveal><div className="section-title">Early-warning levels (open works)</div></Reveal>
        <div className="grid cols-4">
          {["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((lvl) => (
            <div className="card stat" key={lvl}>
              <div className="label">{lvl}</div>
              <div className="value" style={{ fontSize: 26, color: SEV[lvl] || "#9aa8c7" }}>
                {num(w.levels[lvl] || 0)}
              </div>
              <div className="foot">{rupees(w.exposure_by_level?.[lvl] || 0)} exposure</div>
            </div>
          ))}
        </div>
        <p className="muted" style={{ fontSize: 12.5, marginTop: 10 }}>{w.method_note}</p>

        <Reveal><div className="section-title">Lifecycle compliance checks</div></Reveal>
        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>Check</th><th>Authority</th><th>Severity</th>
              <th className="num">Works</th><th>What it means</th>
            </tr></thead>
            <tbody>
              {c.checks.map((chk) => {
                const a = AUTHORITY[chk.authority] || { c: "#9aa8c7", t: chk.authority };
                return (
                  <tr key={chk.key}>
                    <td style={{ fontWeight: 600 }}>{chk.check}</td>
                    <td><span className="badge" style={{ color: a.c, background: "#1a2338" }}>{a.t}</span></td>
                    <td><span style={{ color: SEV[chk.severity] }}>{chk.severity}</span></td>
                    <td className="num">{num(chk.works_affected)}</td>
                    <td className="muted" style={{ fontSize: 12 }}>{chk.meaning}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
