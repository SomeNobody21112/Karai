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

export function Loading() {
  return (
    <div className="loading">
      <div className="spinner" />
      Loading intelligence…
    </div>
  );
}

export function Hitl() {
  return (
    <div className="hitl">
      <span>🛡️</span>
      <span>
        <strong>Investigation leads, not fraud verdicts.</strong> Every item is ranked by
        audit return-on-investment from transparent, corroborated signals. There are no
        fraud labels in this data — a human reviews the evidence and decides what happens.
      </span>
    </div>
  );
}
