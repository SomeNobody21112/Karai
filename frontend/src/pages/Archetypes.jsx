import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, num, rupees } from "../api.js";
import { Loading, Topbar } from "../components/Bits.jsx";

function Bar({ value, color }) {
  return (
    <div className="mini-bar">
      <span style={{ width: `${Math.min(100, value * 100)}%`, background: color }} />
    </div>
  );
}

export default function Archetypes() {
  const [a, setA] = useState(null);
  const [open, setOpen] = useState(null);
  const nav = useNavigate();
  useEffect(() => { api.archetypes().then(setA).catch(console.error); }, []);

  if (!a) return (<><Topbar title="Work Archetypes" /><div className="content"><Loading /></div></>);

  const interpretable = a.filter((x) => x.interpretable !== false).length;
  const maxWorks = Math.max(...a.map((x) => x.n_works));

  return (
    <>
      <Topbar title="Work Archetypes"
        sub="Work types the system discovered on its own from 1.88 lakh descriptions"
        right={<span className="pill">{a.length} archetypes · {interpretable} named</span>} />
      <div className="content">
        <div className="hitl">
          <span>🧩</span>
          <span>
            Nobody told the system these categories exist. It read every description, turned
            each into a 384-number semantic fingerprint, and grouped similar ones. Labels are
            the most distinctive terms in each group — <strong>generated from the actual
            cluster contents</strong>. Where a group turns out to be held together by
            language rather than work type, we say so instead of inventing a name.
          </span>
        </div>

        <div className="arch-list">
          {a.map((x, i) => {
            const isOpen = open === x.archetype_id;
            const uninterpretable = x.interpretable === false;
            return (
              <div className={"arch-card" + (isOpen ? " open" : "")} key={x.archetype_id}>
                <div className="arch-head" onClick={() => setOpen(isOpen ? null : x.archetype_id)}>
                  <div className="arch-rank">{String(i + 1).padStart(2, "0")}</div>

                  <div className="arch-main">
                    <div className="arch-name">
                      {uninterpretable
                        ? <span className="muted">{x.label}</span>
                        : x.label}
                      {uninterpretable && <span className="fam-tag">not interpretable</span>}
                      {x.note && !uninterpretable && <span className="fam-tag">language-mixed</span>}
                    </div>
                    <div className="arch-sub">
                      {num(x.n_works)} works · {x.states} states · {num(x.agencies)} agencies
                      {x.top_state && <> · mostly {x.top_state}</>}
                    </div>
                    <Bar value={x.n_works / maxWorks} color="#6c8cff" />
                  </div>

                  <div className="arch-metrics">
                    <div className="arch-metric">
                      <span className="m-label">Median size</span>
                      <span className="m-value">{rupees(x.median_amount)}</span>
                    </div>
                    <div className="arch-metric">
                      <span className="m-label">Completed</span>
                      <span className="m-value">{(x.completion_rate * 100).toFixed(0)}%</span>
                    </div>
                    <div className="arch-metric">
                      <span className="m-label">Typical duration</span>
                      <span className="m-value">
                        {x.median_days_to_complete ? `${Math.round(x.median_days_to_complete)}d` : "—"}
                      </span>
                    </div>
                    <div className="arch-metric">
                      <span className="m-label">Flagged</span>
                      <span className="m-value" style={{ color: x.lead_rate > 0.25 ? "#ffb340" : undefined }}>
                        {(x.lead_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="arch-metric">
                      <span className="m-label">₹ Exposure</span>
                      <span className="m-value">{rupees(x.total_exposure)}</span>
                    </div>
                  </div>
                  <div className="arch-chev">{isOpen ? "▾" : "▸"}</div>
                </div>

                {isOpen && (
                  <div className="arch-body">
                    {x.note && <p className="arch-note">⚠ {x.note}</p>}
                    {x.top_terms && (
                      <div>
                        <div className="m-label" style={{ marginBottom: 6 }}>
                          Distinctive terms in this cluster
                        </div>
                        <div className="chips">
                          {x.top_terms.split(",").slice(0, 8).map((t) => (
                            <span className="chip" key={t}>{t.trim()}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    <button className="btn" style={{ marginTop: 14 }}
                      onClick={(e) => { e.stopPropagation(); nav("/worklist"); }}>
                      View flagged works in the queue →
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
