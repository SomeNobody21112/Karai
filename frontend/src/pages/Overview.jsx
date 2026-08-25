import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api, num, rupees } from "../api.js";
import { Hitl, Loading, Topbar } from "../components/Bits.jsx";

function Stat({ label, value, foot, accent }) {
  return (
    <div className="card stat">
      <div className="label">{label}</div>
      <div className={"value" + (accent ? " accent" : "")}>{value}</div>
      {foot && <div className="foot">{foot}</div>}
    </div>
  );
}

const BAND_COLOR = { HIGH: "#ff5c6c", MEDIUM: "#ffb648", LOW: "#6fb1ff", NONE: "#33415e" };

export default function Overview() {
  const [stats, setStats] = useState(null);
  const nav = useNavigate();

  useEffect(() => {
    api.stats().then(setStats).catch(console.error);
  }, []);

  if (!stats) return (<><Topbar title="National Overview" /><div className="content"><Loading /></div></>);

  const n = stats.national;
  const bands = ["HIGH", "MEDIUM", "LOW", "NONE"].map((b) => ({
    band: b, works: n.bands[b] || 0,
  }));
  const topStates = stats.by_state.slice(0, 10).map((s) => ({
    state: s.state_name.length > 14 ? s.state_name.slice(0, 13) + "…" : s.state_name,
    full: s.state_name,
    exposure: +(s.exposure / 1e7).toFixed(1),
    leads: s.leads,
  }));

  return (
    <>
      <Topbar
        title="National Overview"
        sub="MPLADS / eSAKSHI · 17th & 18th Lok Sabha · Rajya Sabha"
        right={<span className="pill">Snapshot 2026-05-26</span>}
      />
      <div className="content">
        <Hitl />

        <div className="grid cols-4">
          <Stat label="Works monitored" value={num(n.total_works)}
            foot={`${num(n.completed)} completed · ${num(n.open)} open`} />
          <Stat label="Total recommended" value={rupees(n.total_recommended_rupees)}
            foot={`${n.states} states · ${num(n.implementing_agencies)} agencies`} />
          <Stat label="₹ exposure at risk" value={rupees(n.total_exposure_rupees)} accent
            foot="Completion-risk weighted · not loss, not spend" />
          <Stat label="Investigation leads" value={num(n.surfaced_leads)}
            foot={`${num(n.bands.HIGH || 0)} high-confidence (3+ signal families)`} />
        </div>

        <div className="grid cols-2" style={{ marginTop: 16 }}>
          <div className="card">
            <h3>₹ Exposure by state (top 10, ₹ crore)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topStates} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" stroke="#63718f" fontSize={11}
                  tickFormatter={(v) => `${v}`} />
                <YAxis type="category" dataKey="state" stroke="#93a1bd" fontSize={11} width={90} />
                <Tooltip
                  contentStyle={{ background: "#1a2336", border: "1px solid #2a3752", borderRadius: 8, fontSize: 12 }}
                  formatter={(v, k) => k === "exposure" ? [`₹${v} Cr`, "Exposure"] : [v, k]}
                  labelFormatter={(_, p) => p?.[0]?.payload?.full} />
                <Bar dataKey="exposure" radius={[0, 4, 4, 0]} fill="#4f8cff" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3>Confidence bands</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={bands} margin={{ left: 0, right: 10 }}>
                <XAxis dataKey="band" stroke="#93a1bd" fontSize={11} />
                <YAxis stroke="#63718f" fontSize={11}
                  tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v} />
                <Tooltip
                  contentStyle={{ background: "#1a2336", border: "1px solid #2a3752", borderRadius: 8, fontSize: 12 }}
                  formatter={(v) => [num(v), "Works"]} cursor={{ fill: "#ffffff08" }} />
                <Bar dataKey="works" radius={[4, 4, 0, 0]}>
                  {bands.map((b) => <Cell key={b.band} fill={BAND_COLOR[b.band]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="legend">
              <span><i className="dot" style={{ background: "#ff5c6c" }} /> HIGH ≥3 families</span>
              <span><i className="dot" style={{ background: "#ffb648" }} /> MEDIUM 2</span>
              <span><i className="dot" style={{ background: "#6fb1ff" }} /> LOW 1</span>
            </div>
          </div>
        </div>

        <div className="section-title">Learned work archetypes (top 20 of 50)</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>#</th><th>Archetype (auto-labelled by distinctive terms)</th><th className="num">Works</th></tr>
            </thead>
            <tbody>
              {stats.archetypes.map((a, i) => (
                <tr key={a.archetype_id} onClick={() => nav(`/worklist`)}>
                  <td className="rank">{i + 1}</td>
                  <td>{a.label}</td>
                  <td className="num">{num(a.n_works)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
