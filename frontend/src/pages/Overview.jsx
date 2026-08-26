import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api, num, rupees } from "../api.js";
import { Hitl, Loading, Topbar } from "../components/Bits.jsx";
import { CountUp, Reveal } from "../components/Reveal.jsx";
import { usePointerSpotlight } from "../hooks.js";
import { useRole } from "../RoleContext.jsx";
import Insight from "../components/Insight.jsx";
import { useI18n } from "../I18nContext.jsx";

const BAND_COLOR = { HIGH: "#a8452a", MEDIUM: "#9a6b1f", LOW: "#a8452a", NONE: "#ddd5c6" };
const TIP = {
  background: "#ffffff", border: "1px solid #ddd5c6", borderRadius: 3,
  fontSize: 12, boxShadow: "0 2px 10px rgba(60,48,30,.12)",
};

function Stat({ label, value, foot, accent, danger, delay = 0 }) {
  const ref = usePointerSpotlight();
  return (
    <Reveal delay={delay}>
      <div className="card stat spot" ref={ref}>
        <div className="label">{label}</div>
        <div className={"value" + (accent ? " accent" : "") + (danger ? " danger" : "")}>{value}</div>
        {foot && <div className="foot">{foot}</div>}
      </div>
    </Reveal>
  );
}

export default function Overview() {
  const [stats, setStats] = useState(null);
  const nav = useNavigate();
  const { params, role, scope } = useRole();
  const { t } = useI18n();

  useEffect(() => {
    setStats(null);
    api.stats(params).then(setStats).catch(console.error);
  }, [role, scope]);

  if (!stats)
    return (<><Topbar title={t("overview.title", "National Overview")} /><div className="content"><Loading /></div></>);

  const n = stats.national;
  const bands = ["HIGH", "MEDIUM", "LOW", "NONE"].map((b) => ({ band: b, works: n.bands[b] || 0 }));
  const topStates = (stats.by_state || []).slice(0, 10).map((s) => ({
    state: s.state_name.length > 14 ? s.state_name.slice(0, 13) + "…" : s.state_name,
    full: s.state_name,
    exposure: +(s.exposure / 1e7).toFixed(1),
  }));

  return (
    <>
      <Topbar
        title={t("overview.title", "National Overview")}
        sub={scope ? `Scoped to ${scope}` : "MPLADS / eSAKSHI · 17th & 18th Lok Sabha · Rajya Sabha"}
        right={<span className="pill live">Snapshot 2026-05-26</span>}
      />
      <div className="content">
        <Hitl />
        <Insight kind="portfolio" params={params} />

        <div className="grid cols-4">
          <Stat
            label={t("overview.worksMonitored", "Works monitored")}
            value={<CountUp end={n.total_works} />}
            foot={`${num(n.completed)} ${t("overview.completed", "completed")} · ${num(n.open)} ${t("overview.open", "open")}`}
          />
          <Stat
            delay={80}
            label={t("overview.totalRecommended", "Total recommended")}
            value={<CountUp end={n.total_recommended_rupees / 1e7}
              format={(v) => `₹${v.toLocaleString("en-IN")} Cr`} />}
            foot={`${n.states} states · ${num(n.implementing_agencies)} agencies`}
          />
          <Stat
            delay={160}
            accent
            label={t("overview.exposure", "Exposure at risk")}
            value={<CountUp end={n.total_exposure_rupees / 1e7}
              format={(v) => `₹${v.toLocaleString("en-IN")} Cr`} />}
            foot={t("overview.exposureFoot", "Completion-risk weighted, not loss, not spend")}
          />
          <Stat
            delay={240}
            label={t("overview.leads", "Investigation leads")}
            value={<CountUp end={n.surfaced_leads} />}
            foot={`${num(n.bands.HIGH || 0)} high-confidence (3+ signal families)`}
          />
        </div>

        <div className="grid cols-2" style={{ marginTop: 16 }}>
          <Reveal delay={60}>
            <div className="card">
              <h3>{t("overview.byState", "Exposure by state (top 10, crore)")}</h3>
              <ResponsiveContainer width="100%" height={310}>
                <BarChart data={topStates} layout="vertical" margin={{ left: 6, right: 22 }}>
                  <defs>
                    <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#a8452a" />
                      <stop offset="100%" stopColor="#9a6b1f" />
                    </linearGradient>
                  </defs>
                  <XAxis type="number" stroke="#8a8175" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis type="category" dataKey="state" stroke="#5c554a" fontSize={11}
                    width={94} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={TIP} cursor={{ fill: "rgba(168,69,42,.06)" }}
                    formatter={(v) => [`₹${v} Cr`, "Exposure"]}
                    labelFormatter={(_, p) => p?.[0]?.payload?.full} />
                  <Bar dataKey="exposure" radius={[0, 2, 2, 0]} fill="url(#barGrad)"
                    animationDuration={1100} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Reveal>

          <Reveal delay={140}>
            <div className="card">
              <h3>{t("overview.bands", "Confidence bands")}</h3>
              <ResponsiveContainer width="100%" height={310}>
                <BarChart data={bands} margin={{ left: 0, right: 10 }}>
                  <XAxis dataKey="band" stroke="#5c554a" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#8a8175" fontSize={11} tickLine={false} axisLine={false}
                    tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v)} />
                  <Tooltip contentStyle={TIP} cursor={{ fill: "rgba(168,69,42,.06)" }}
                    formatter={(v) => [num(v), "Works"]} />
                  <Bar dataKey="works" radius={[2, 2, 0, 0]} animationDuration={1100}>
                    {bands.map((b) => <Cell key={b.band} fill={BAND_COLOR[b.band] || "#ddd5c6"} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="legend">
                <span><i className="dot" style={{ background: "#a8452a" }} /> HIGH · 3+ families</span>
                <span><i className="dot" style={{ background: "#9a6b1f" }} /> MEDIUM · 2</span>
                <span><i className="dot" style={{ background: "#a8452a" }} /> LOW · 1</span>
              </div>
            </div>
          </Reveal>
        </div>

        <Reveal><div className="section-title">{t("overview.archetypes", "Learned work archetypes")}</div></Reveal>
        <Reveal delay={70}>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>#</th><th>Archetype (auto-labelled by distinctive terms)</th>
                  <th className="num">Works</th></tr>
              </thead>
              <tbody>
                {(stats.archetypes || []).map((a, i) => (
                  <tr key={a.archetype_id} onClick={() => nav("/archetypes")}
                    style={{ animationDelay: `${i * 22}ms` }}>
                    <td className="rank">{String(i + 1).padStart(2, "0")}</td>
                    <td>{a.label}</td>
                    <td className="num">{num(a.n_works)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Reveal>
      </div>
    </>
  );
}
