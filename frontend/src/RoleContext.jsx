import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api.js";

const Ctx = createContext({ role: "ministry", scope: "", meta: null, setRole: () => {} });

export function RoleProvider({ children }) {
  const [role, setRole] = useState("ministry");
  const [scope, setScope] = useState("");
  const [meta, setMeta] = useState(null);

  useEffect(() => { api.roles().then(setMeta).catch(() => {}); }, []);

  const value = {
    role, scope, meta,
    setRole: (r) => { setRole(r); setScope(""); },
    setScope,
    params: role === "ministry" || !scope ? {} : { role, scope },
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useRole = () => useContext(Ctx);

export function RoleSwitcher() {
  const { role, scope, meta, setRole, setScope } = useRole();
  if (!meta) return null;
  const scopes = meta.scopes[role] || [];
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <select className="select" value={role} onChange={(e) => setRole(e.target.value)}>
        {Object.entries(meta.roles).map(([k, v]) => (
          <option key={k} value={k}>{v.label}</option>
        ))}
      </select>
      {role !== "ministry" && (
        <select className="select" value={scope} onChange={(e) => setScope(e.target.value)}
          style={{ maxWidth: 230 }}>
          <option value="">— select jurisdiction —</option>
          {scopes.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      )}
    </div>
  );
}
