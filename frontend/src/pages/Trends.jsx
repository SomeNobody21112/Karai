import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, num, rupees } from "../api.js";
import { Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";

const STATE_STYLE = {
  NORMAL: { c: "#6c8cff", t: "Normal" },
  EMERGING: { c: "#35d9a6", t: "Emerging" },
  GROWING: { c: "#35d9a6", t: "Growing" },
  STABLE: { c: "#6c8cff", t: "Stable" },
  DECLINING: { c: "#ffb340", t: "Declining" },
  SUDDEN_CHANGE: { c: "#ff5f7a", t: "Sudden change" },
  PERSISTENT_CHANGE: { c: "#ffb340", t: "Persistent change" },
  INSUFFICIENT_HISTORY: { c: "#5f6d8d", t: "Insufficient history" },
};

function Tag({ value }) {
  const s = STATE_STYLE[value] || { c: "#5f6d8d", t: value };
  return (
    <span className="badge" style={{ color: s.c, background: "#1a2338" }}>{s.t}</span>
  );
}

export default function Trends() {
  const [d, setD] = useState(null);
  useEffect(() => { api.temporal().then(setD).catch(console.error); }, []);

  if (!d) return (<><Topbar title="Temporal Intelligence" /><div className="content"><Loading /></div></>);

  const series = d.national_series.map((s) => ({
    period: s.period, works: s.works,
    median: s.median_amount ? Math.round(s.median_amount / 1000) : null,
  }));

  return (
    <>
      <Topbar title="Temporal Intelligence"
        sub="How the scheme is changing over time"
        right={<span className="pill">{num(d.counts.agencies_analysed)} agencies analysed</span>} />
      <div className="content">
        <div className="hitl">
          <span>📈</span>
          <span>
            <strong>Method:</strong> {d.method_note}
          </span>
        </div>

        <Reveal><div className="grid cols-2">
          <div className="card">
            <h3>National monthly work volume</h3>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={series}>
                <CartesianGrid stroke="#1b2439" vertical={false} />
                <XAxis dataKey="period" stroke="#5f6d8d" fontSize={10} minTickGap={30} />
                <YAxis stroke="#5f6d8d" fontSize={11} />
                <Tooltip contentStyle={{ background: "#141b2d", border: "1px solid #2a3752", borderRadius: 8, fontSize: 12 }} />
                <Line type="monotone" dataKey="works" stroke="#6c8cff" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <div style={{ marginTop: 10 }}>
              <Tag value={d.national_volume.classification} />
              <span className="muted" style={{ fontSize: 12.5, marginLeft: 10 }}>
                {d.national_volume.explanation}
              </span>
            </div>
          </div>

          <div className="card">
            <h3>National median recommended amount (₹ thousand)</h3>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={series}>
                <CartesianGrid stroke="#1b2439" vertical={false} />
                <XAxis dataKey="period" stroke="#5f6d8d" fontSize={10} minTickGap={30} />
                <YAxis stroke="#5f6d8d" fontSize={11} />
                <Tooltip contentStyle={{ background: "#141b2d", border: "1px solid #2a3752", borderRadius: 8, fontSize: 12 }} />
                <Line type="monotone" dataKey="median" stroke="#35d9a6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <div style={{ marginTop: 10 }}>
              <Tag value={d.national_amount.classification} />
              <span className="muted" style={{ fontSize: 12.5, marginLeft: 10 }}>
                {d.national_amount.explanation}
              </span>
            </div>
          </div>
        </div>

        </Reveal>
        <Reveal><div className="section-title">Emerging Public Works Radar</div></Reveal>
        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>Work type</th><th>Status</th>
              <th className="num">Recent works</th><th className="num">Share change</th>
            </tr></thead>
            <tbody>
              {d.archetype_radar.slice(0, 12).map((a) => (
                <tr key={a.archetype_id}>
                  <td>{a.label}</td>
                  <td><Tag value={a.classification} /></td>
                  <td className="num">{num(a.recent_works)}</td>
                  <td className="num" style={{ color: a.delta >= 0 ? "#35d9a6" : "#ffb340" }}>
                    {a.delta >= 0 ? "+" : ""}{(a.delta * 100).toFixed(2)} pp
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="section-title">
          Agencies whose behaviour changed ({num(d.counts.agencies_changed)} of {num(d.counts.agencies_analysed)})
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>Implementing agency</th><th>Status</th>
              <th className="num">Total works</th><th>Why flagged</th>
            </tr></thead>
            <tbody>
              {d.agency_trends.slice(0, 20).map((a) => (
                <tr key={a.entity}>
                  <td className="desc-cell">{a.entity}</td>
                  <td><Tag value={a.classification} /></td>
                  <td className="num">{num(a.total_works)}</td>
                  <td className="muted" style={{ fontSize: 12 }}>{a.explanation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
