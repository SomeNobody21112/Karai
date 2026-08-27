import { sev } from "../severity.js";

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

/**
 * A severity level, shown three ways at once: colour, glyph and its written label.
 * Colour is the redundant channel here, never the load-bearing one — red and amber
 * collapse together under deuteranopia, so the shape and the word are what a
 * reviewer actually reads.
 */
export function Band({ value, label }) {
  const level = String(value || "").toUpperCase();
  const { glyph } = sev(level);
  return (
    <span className={`badge sev ${level}`} title={`Severity: ${label || value}`}>
      <i className="glyph" aria-hidden="true">{glyph}</i>
      {label || value}
    </span>
  );
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

export function Hitl({ text }) {
  return (
    <div className="hitl">
      <span style={{ fontSize: 15, color: "var(--brick)" }}>◈</span>
      <span>{text || (
        <><strong>Investigation leads, not verdicts.</strong> Every item is ranked by audit
        return-on-investment from transparent, corroborated signals. A human reviews the
        evidence and decides what happens.</>
      )}</span>
    </div>
  );
}
