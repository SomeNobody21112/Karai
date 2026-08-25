import { NavLink, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview.jsx";
import Worklist from "./pages/Worklist.jsx";
import CaseFile from "./pages/CaseFile.jsx";
import HowItWorks from "./pages/HowItWorks.jsx";

function Sidebar() {
  const link = ({ isActive }) => "nav-link" + (isActive ? " active" : "");
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">M</div>
        <div>
          <div className="brand-name">MPLADS Intel</div>
          <div className="brand-sub">Forensic Monitoring</div>
        </div>
      </div>
      <NavLink to="/" end className={link}>
        <span className="ic">◫</span> Overview
      </NavLink>
      <NavLink to="/worklist" className={link}>
        <span className="ic">☰</span> Audit Worklist
      </NavLink>
      <NavLink to="/how" className={link}>
        <span className="ic">💡</span> How it works
      </NavLink>
      <div className="sidebar-foot">
        Learn → Compare → Predict → Explain → Prioritise
        <br />
        <br />
        Investigation leads, not fraud verdicts. A human decides every action.
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <div className="shell">
      <Sidebar />
      <div className="main">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/worklist" element={<Worklist />} />
          <Route path="/how" element={<HowItWorks />} />
          <Route path="/case/:ref" element={<CaseFile />} />
        </Routes>
      </div>
    </div>
  );
}
