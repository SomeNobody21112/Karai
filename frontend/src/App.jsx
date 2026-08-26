import { useEffect } from "react";
import { NavLink, Route, Routes, useLocation } from "react-router-dom";
import Landing from "./pages/Landing.jsx";
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
import { useScrollProgress } from "./hooks.js";
import { LanguageSwitcher } from "./I18nContext.jsx";
import Chat from "./components/Chat.jsx";
import Logo from "./components/Logo.jsx";
import { useI18n } from "./I18nContext.jsx";

const NAV = [
  {
    key: "nav.monitor", label: "Monitor",
    items: [
      { to: "/overview", ic: "▤", key: "nav.overview", label: "Overview" },
      { to: "/worklist", ic: "▦", key: "nav.worklist", label: "Investigation Queue" },
    ],
  },
  {
    key: "nav.intelligence", label: "Intelligence",
    items: [
      { to: "/trends", ic: "◪", key: "nav.trends", label: "Temporal" },
      { to: "/duplicates", ic: "⧉", key: "nav.duplicates", label: "Near-Duplicates" },
      { to: "/compliance", ic: "§", key: "nav.compliance", label: "Compliance" },
      { to: "/archetypes", ic: "◈", key: "nav.archetypes", label: "Work Archetypes" },
    ],
  },
  {
    key: "nav.trust", label: "Trust",
    items: [
      { to: "/transparency", ic: "◉", key: "nav.transparency", label: "Data Transparency" },
      { to: "/how", ic: "?", key: "nav.how", label: "How it works" },
    ],
  },
];

function Sidebar() {
  const link = ({ isActive }) => "nav-link" + (isActive ? " active" : "");
  const { role, scope, meta } = useRole();
  const { t } = useI18n();
  return (
    <aside className="sidebar">
      <NavLink to="/" className="brand">
        <Logo size={38} className="brand-logo" />
        <div>
          <div className="brand-name">MPLADS Intelligence</div>
          <div className="brand-sub">{t("shell.brandSub", "Forensic Monitoring")}</div>
        </div>
      </NavLink>

      {NAV.map((group) => (
        <div key={group.key}>
          <div className="nav-group-label">{t(group.key, group.label)}</div>
          {group.items.map((item) => (
            <NavLink key={item.to} to={item.to} className={link}>
              <span className="ic">{item.ic}</span> {t(item.key, item.label)}
            </NavLink>
          ))}
        </div>
      ))}

      <div className="sidebar-foot">
        {meta && (
          <div style={{ marginBottom: 12 }}>
            {t("shell.viewingAs", "Viewing as")}{" "}
            <b style={{ color: "var(--text-2)" }}>{meta.roles[role]?.label}</b>
            {scope && <> · {scope}</>}
          </div>
        )}
        {t("shell.chain", "Learn, Compare, Predict, Explain, Prioritise")}
        <br />
        <br />
        {t("shell.leadsNotVerdicts",
           "Investigation leads, not fraud verdicts. A human decides every action.")}
      </div>
    </aside>
  );
}

/** Scroll to top whenever the route changes — dashboards should not inherit scroll. */
function ScrollReset() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
  }, [pathname]);
  return null;
}

function Shell() {
  const { pathname } = useLocation();
  const { t } = useI18n();
  const progress = useScrollProgress();
  const isLanding = pathname === "/";

  return (
    <>
      <div className="scroll-progress" style={{ width: `${progress * 100}%` }} />
      <ScrollReset />
      {isLanding ? (
        <Routes>
          <Route path="/" element={<Landing />} />
        </Routes>
      ) : (
        <div className="shell">
          <Sidebar />
          <div className="main">
            <div className="role-bar">
              <span className="muted" style={{ fontSize: 12 }}>
                {t("shell.stakeholder", "Stakeholder view")}
              </span>
              <RoleSwitcher />
              <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 14 }}>
                <LanguageSwitcher />
              </div>
              <span className="muted" style={{ fontSize: 11 }}>
                {t("shell.roleSim", "Role simulation — no authentication in this prototype")}
              </span>
            </div>
            <Routes>
              <Route path="/overview" element={<Overview />} />
              <Route path="/worklist" element={<Worklist />} />
              <Route path="/trends" element={<Trends />} />
              <Route path="/duplicates" element={<Duplicates />} />
              <Route path="/compliance" element={<Compliance />} />
              <Route path="/archetypes" element={<Archetypes />} />
              <Route path="/transparency" element={<Transparency />} />
              <Route path="/how" element={<HowItWorks />} />
              <Route path="/case/:ref" element={<CaseFile />} />
            </Routes>
            <Chat />
          </div>
        </div>
      )}
    </>
  );
}

export default function App() {
  return (
    <RoleProvider>
      <Shell />
    </RoleProvider>
  );
}
