import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, num, rupees } from "../api.js";
import { Band, Hitl, Loading, SkeletonRows, Topbar } from "../components/Bits.jsx";
import { useRole } from "../RoleContext.jsx";

const PAGE = 25;

export default function Worklist() {
  const [data, setData] = useState(null);
  const [states, setStates] = useState([]);
  const [q, setQ] = useState("");
  const [state, setState] = useState("");
  const [band, setBand] = useState("");
  const [page, setPage] = useState(0);
  const nav = useNavigate();
  const { params, role, scope } = useRole();

  useEffect(() => { api.states().then(setStates).catch(() => {}); }, []);

  useEffect(() => {
    setData(null);
    const t = setTimeout(() => {
      api.worklist({ limit: PAGE, offset: page * PAGE, q, state, band, ...params })
        .then(setData).catch(console.error);
    }, 200);
    return () => clearTimeout(t);
  }, [q, state, band, page, role, scope]);

  useEffect(() => { setPage(0); }, [q, state, band, role, scope]);

  const total = data?.total ?? 0;
  const pages = Math.ceil(total / PAGE);

  return (
    <>
      <Topbar
        title="Investigation Queue"
        sub="Ranked by Audit-ROI = priority × ₹ exposure × corroboration"
        right={<span className="pill">{num(total)} leads</span>}
      />
      <div className="content">
        <Hitl />
        <div className="card" style={{ marginBottom: 18, fontSize: 13.5, color: "var(--text-2)" }}>
          <strong style={{ color: "var(--text)" }}>What this list is:</strong> every work below was
          flagged by <strong>at least two independent kinds of evidence</strong>. It is ordered so
          the works with the most money-at-risk per hour of audit are on top. Click any row to see
          the full reason and the recommended next step. Nothing here is an accusation.
        </div>
        <div className="toolbar">
          <input className="input" placeholder="Search description or implementing agency…"
            value={q} onChange={(e) => setQ(e.target.value)} />
          <select className="select" value={state} onChange={(e) => setState(e.target.value)}>
            <option value="">All states</option>
            {states.map((s) => <option key={s.state_name} value={s.state_name}>{s.state_name}</option>)}
          </select>
          <select className="select" value={band} onChange={(e) => setBand(e.target.value)}>
            <option value="">All bands</option>
            <option value="HIGH">HIGH (3+ families)</option>
            <option value="MEDIUM">MEDIUM (2 families)</option>
          </select>
        </div>

        {!data ? <SkeletonRows rows={8} /> : data.items.length === 0 ? (
          <div className="empty">No leads match these filters.</div>
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th><th>Work</th><th>State</th><th>Confidence</th>
                    <th className="num">Amount</th><th className="num">₹ Exposure</th>
                    <th className="num">Audit-ROI</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((r, i) => (
                    <tr key={r.work_ref} onClick={() => nav(`/case/${r.work_ref}`)}
                      style={{ animationDelay: `${i * 26}ms` }}>
                      <td className="rank">{page * PAGE + i + 1}</td>
                      <td>
                        <div className="desc-cell">{r.description || "—"}</div>
                        <div className="muted" style={{ fontSize: 11 }}>
                          {r.archetype} · {r.n_families} signal families
                        </div>
                      </td>
                      <td className="muted">{r.state}</td>
                      <td><Band value={r.band} /></td>
                      <td className="num">{rupees(r.recommended_amount)}</td>
                      <td className="num">{rupees(r.exposure_rupees)}</td>
                      <td className="num" style={{ fontWeight: 700, color: "#bacdff" }}>
                        {rupees(r.audit_roi)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pager">
              <span className="muted">
                Page {page + 1} of {pages} · showing {data.items.length} of {num(total)}
              </span>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn" disabled={page === 0} onClick={() => setPage(page - 1)}>← Prev</button>
                <button className="btn" disabled={page + 1 >= pages} onClick={() => setPage(page + 1)}>Next →</button>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
