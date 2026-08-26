import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, num, rupees } from "../api.js";
import { Loading, Topbar } from "../components/Bits.jsx";

export default function Archetypes() {
  const [a, setA] = useState(null);
  const nav = useNavigate();
  useEffect(() => { api.archetypes().then(setA).catch(console.error); }, []);

  if (!a) return (<><Topbar title="Work Archetypes" /><div className="content"><Loading /></div></>);

  return (
    <>
      <Topbar title="Work Archetypes"
        sub="Work types the system discovered on its own from 1.88 lakh descriptions"
        right={<span className="pill">{a.length} archetypes</span>} />
      <div className="content">
        <div className="hitl">
          <span>🧩</span>
          <span>
            Nobody told the system these categories exist. It read every work description,
            turned it into a 384-number semantic fingerprint, and grouped similar ones. Labels
            are the most distinctive terms in each group — <strong>generated from the actual
            cluster contents, never invented</strong>.
          </span>
        </div>

        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>#</th><th>Archetype</th><th className="num">Works</th>
              <th className="num">States</th><th className="num">Median amount</th>
              <th className="num">Completion</th><th className="num">Median days</th>
              <th className="num">Lead rate</th><th className="num">₹ Exposure</th>
            </tr></thead>
            <tbody>
              {a.map((x, i) => (
                <tr key={x.archetype_id} onClick={() => nav("/worklist")}>
                  <td className="rank">{i + 1}</td>
                  <td>
                    <div style={{ fontWeight: 600 }}>{x.label}</div>
                    <div className="muted" style={{ fontSize: 11 }}>
                      mostly {x.top_state} · {num(x.agencies)} agencies
                    </div>
                  </td>
                  <td className="num">{num(x.n_works)}</td>
                  <td className="num">{x.states}</td>
                  <td className="num">{rupees(x.median_amount)}</td>
                  <td className="num">{(x.completion_rate * 100).toFixed(0)}%</td>
                  <td className="num">
                    {x.median_days_to_complete ? Math.round(x.median_days_to_complete) : "—"}
                  </td>
                  <td className="num" style={{ color: x.lead_rate > 0.25 ? "#ffb648" : "inherit" }}>
                    {(x.lead_rate * 100).toFixed(0)}%
                  </td>
                  <td className="num">{rupees(x.total_exposure)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
