import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, num, rupees } from "../api.js";
import { Band, Loading, Topbar } from "../components/Bits.jsx";

const FAM_ICON = { amount: "₹", duration: "⏱", lifecycle: "⚑", behaviour: "📈" };

function Meter({ value, color }) {
  return (
    <div className="meter">
      <span style={{ width: `${Math.round(value * 100)}%`, background: color }} />
    </div>
  );
}

export default function CaseFile() {
  const { ref } = useParams();
  const [c, setC] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    setC(null); setErr(null);
    api.case(ref).then(setC).catch((e) => setErr(String(e)));
  }, [ref]);

  if (err) return (<><Topbar title="Case File" /><div className="content"><div className="empty">{err}</div></div></>);
  if (!c) return (<><Topbar title="Case File" /><div className="content"><Loading /></div></>);

  const id = c.identity;
  return (
    <>
      <Topbar title="Case File" sub={c.work_ref}
        right={<Band value={c.confidence_band} />} />
      <div className="content">
        <Link to="/worklist" className="back">← Back to worklist</Link>

        <div className="card" style={{ marginBottom: 18, fontSize: 13.5, color: "var(--text-dim)" }}>
          <strong style={{ color: "var(--text)" }}>Plain summary:</strong> this work was put on the
          audit list because {c.n_signal_families} independent kinds of evidence agreed something is
          worth checking. About <strong>{rupees(c.exposure_rupees)}</strong> may be tied up if it does
          not finish. Read the evidence below, then see the recommended next step for a human.
        </div>

        <div className="case-head">
          <div>
            <div className="case-title">{id.description || "MPLADS Work"}</div>
            <div className="case-meta">
              {id.state} · {id.constituency} · {id.implementing_agency}
            </div>
            <div className="case-meta">
              MP: {id.mp_name} · Recommended {id.recommendation_date || "—"} · Status: {id.status}
            </div>
          </div>
          <div className="roi-badge">
            <div className="v">{rupees(c.audit_roi)}</div>
            <div className="l">Audit-ROI rank score</div>
          </div>
        </div>

        <div className="grid cols-4" style={{ marginTop: 20 }}>
          <div className="card stat">
            <div className="label">Recommended</div>
            <div className="value" style={{ fontSize: 24 }}>{rupees(id.recommended_amount)}</div>
          </div>
          <div className="card stat">
            <div className="label">₹ Exposure at risk</div>
            <div className="value accent" style={{ fontSize: 24 }}>{rupees(c.exposure_rupees)}</div>
            <div className="foot">amount × completion risk</div>
          </div>
          <div className="card stat">
            <div className="label">Completion risk</div>
            <div className="value" style={{ fontSize: 24 }}>{Math.round(c.risk.completion_risk * 100)}%</div>
            <Meter value={c.risk.completion_risk} color="#ffb648" />
            <div className="foot">basis: {c.risk.basis}</div>
          </div>
          <div className="card stat">
            <div className="label">Corroboration</div>
            <div className="value" style={{ fontSize: 24 }}>{c.n_signal_families} families</div>
            <div className="foot">independent signal families fired</div>
          </div>
        </div>

        <div className="grid cols-2" style={{ marginTop: 16 }}>
          <div className="card">
            <h3>Evidence — why this was surfaced</h3>
            {c.evidence.map((e, i) => (
              <div className="evidence-item" key={i}>
                <div className="evidence-icon">{FAM_ICON[e.family] || "•"}</div>
                <div className="evidence-body">
                  <div className="s">{e.signal}<span className="fam-tag">{e.family}</span></div>
                  <div className="d">{e.detail}</div>
                </div>
              </div>
            ))}
          </div>

          <div>
            <div className="card" style={{ marginBottom: 16 }}>
              <h3>Peer context</h3>
              <dl className="kv">
                <dt>Archetype</dt><dd>{c.archetype.label}</dd>
                <dt>Peer level</dt><dd>{c.peer_context.level}</dd>
                <dt>Peer group size</dt><dd>{num(c.peer_context.group_size)} works</dd>
                <dt>Amount percentile</dt>
                <dd>{c.peer_context.amount_percentile != null
                  ? `${Math.round(c.peer_context.amount_percentile * 100)}th` : "—"}</dd>
                <dt>Priority score</dt><dd>{c.priority.toFixed(3)}</dd>
              </dl>
            </div>

            <div className="action-panel">
              <div className="label">Recommended next step</div>
              <div className="text">{c.recommended_next_step}</div>
              <div className="note">
                This is an investigation lead, not a fraud finding. The system recommends
                where to look; a human authority decides what happens next.
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
