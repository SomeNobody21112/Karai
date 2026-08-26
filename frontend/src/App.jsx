import { NavLink, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview.jsx";
import Worklist from "./pages/Worklist.jsx";
import CaseFile from "./pages/CaseFile.jsx";
import HowItWorks from "./pages/HowItWorks.jsx";
import Trends from "./pages/Trends.jsx";
import Duplicates from "./pages/Duplicates.jsx";
import Compliance from "./pages/Compliance.jsx";
import Transparency from "./pages/Transparency.jsx";
import Archetypes from "./pages/Archetypes.jsx";
import { RoleProvider, RoleSwitcher, useRole } from "./RoleContext.jsx";

const NAV = [
  { to: "/", ic: "◫", label: "Overview", end: true },
  { to: "/worklist", ic: "☰", label: "Investigation Queue" },
  { to: "/trends", ic: "📈", label: "Temporal Intelligence" },
  { to: "/duplicates", ic: "⧉", label: "Near-Duplicates" },
  { to: "/compliance", ic: "⚖", label: "Compliance & Warning" },
  { to: "/archetypes", ic: "🧩", label: "Work Archetypes" },
  { to: "/transparency", ic: "🔒", label: "Data Transparency" },
  { to: "/how", ic: "💡", label: "How it works" },
];

function Sidebar() {
  const link = ({ isActive }) => "nav-link" + (isActive ? " active" : "");
  const { role, scope, meta } = useRole();
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">M</div>
        <div>
          <div className="brand-name">MPLADS Intel</div>
          <div className="brand-sub">Forensic Monitoring</div>
        </div>
      </div>
      {NAV.map((n) => (
        <NavLink key={n.to} to={n.to} end={n.end} className={link}>
          <span className="ic">{n.ic}</span> {n.label}
        </NavLink>
      ))}
      <div className="sidebar-foot">
        {meta && (
          <div style={{ marginBottom: 10 }}>
            Viewing as <strong style={{ color: "var(--text-dim)" }}>
              {meta.roles[role]?.label}
            </strong>
            {scope && <> · {scope}</>}
          </div>
        )}
        Learn → Compare → Predict → Explain → Prioritise
        <br /><br />
        Investigation leads, not fraud verdicts. A human decides every action.
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <RoleProvider>
      <div className="shell">
        <Sidebar />
        <div className="main">
          <div className="role-bar">
            <span className="muted" style={{ fontSize: 12 }}>Stakeholder view</span>
            <RoleSwitcher />
            <span className="muted" style={{ fontSize: 11, marginLeft: "auto" }}>
              Role simulation — no authentication in this prototype
            </span>
          </div>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/worklist" element={<Worklist />} />
            <Route path="/trends" element={<Trends />} />
            <Route path="/duplicates" element={<Duplicates />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/archetypes" element={<Archetypes />} />
            <Route path="/transparency" element={<Transparency />} />
            <Route path="/how" element={<HowItWorks />} />
            <Route path="/case/:ref" element={<CaseFile />} />
          </Routes>
        </div>
      </div>
    </RoleProvider>
  );
}
