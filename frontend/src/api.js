const base = "";

async function get(path) {
  const res = await fetch(base + path);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  stats: () => get("/api/stats"),
  states: () => get("/api/states"),
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
