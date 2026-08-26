const base = "";

async function get(path) {
  const res = await fetch(base + path);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  stats: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/stats?${q}`);
  },
  states: () => get("/api/states"),
  models: () => get("/api/models"),
  roles: () => get("/api/roles"),
  languages: () => get("/api/languages"),
  strings: (lang) => get(`/api/strings?lang=${encodeURIComponent(lang)}`),
  portfolioInsight: (p = {}) => {
    const q = new URLSearchParams(
      Object.entries(p).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/insight/portfolio?${q}`);
  },
  caseInsight: (ref, lang = "en") =>
    get(`/api/insight/case/${encodeURIComponent(ref)}?lang=${encodeURIComponent(lang)}`),
  temporal: () => get("/api/temporal"),
  transparency: () => get("/api/transparency"),
  compliance: () => get("/api/compliance"),
  earlyWarning: () => get("/api/early-warning"),
  healthIndex: () => get("/api/health-index"),
  archetypes: () => get("/api/archetypes"),
  duplicates: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/duplicates?${q}`);
  },
  worklist: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/worklist?${q}`);
  },
  case: (ref) => get(`/api/case/${encodeURIComponent(ref)}`),
};

export function rupees(n) {
  if (n == null) return "—";
  if (n >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`;
  if (n >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`;
  if (n >= 1e3) return `₹${(n / 1e3).toFixed(0)}K`;
  return `₹${Math.round(n)}`;
}

export function num(n) {
  return n == null ? "—" : Number(n).toLocaleString("en-IN");
}
