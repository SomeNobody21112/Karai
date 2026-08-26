export function Topbar({ title, sub, right }) {
  return (
    <div className="topbar">
      <div>
        <h1>{title}</h1>
        {sub && <div className="sub">{sub}</div>}
      </div>
      {right}
    </div>
  );
}

export function Band({ value }) {
  return <span className={`badge ${value}`}>{value}</span>;
}

export function Loading({ label = "Loading intelligence" }) {
  return (
    <div className="loading">
      <div className="spinner" />
      {label}…
    </div>
  );
}

/** Shimmering placeholder rows — used while a table loads. */
export function SkeletonRows({ rows = 6, height = 46 }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height, opacity: 1 - i * 0.09 }} />
      ))}
    </div>
  );
}

export function Hitl() {
  return (
    <div className="hitl">
      <span style={{ fontSize: 16 }}>🛡️</span>
      <span>
        <strong>Investigation leads, not fraud verdicts.</strong> Every item is ranked by
        audit return-on-investment from transparent, corroborated signals. There are no
        fraud labels in this data — a human reviews the evidence and decides what happens.
      </span>
    </div>
  );
}
