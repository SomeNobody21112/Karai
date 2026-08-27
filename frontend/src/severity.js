/**
 * The one severity scale. Every band, level and classification in the UI resolves
 * through here — six pages used to each keep their own copy, which is how HIGH and
 * LOW ended up painted the same terracotta in two of them.
 *
 * Traffic-light hues, because that is what a reviewer already knows how to read.
 * They are chosen against the parchment ground (#f7f4ed), not picked by eye:
 *
 *   level     fill      vs ground   ink        on its chip   glyph
 *   CRITICAL  #8f1d14   8.12:1      #7d1d12    8.27:1        ■
 *   HIGH      #d13a2a   4.40:1      #a8301f    5.66:1        ▲
 *   MEDIUM    #b58200   3.10:1      #8a6508    4.62:1        ◆
 *   LOW       #43976a   3.25:1      #2b6b47    5.31:1        ●
 *
 * `fill` clears the 3:1 floor for a chart mark; `ink` clears 4.5:1 for label text
 * on `soft`. Red and amber cannot be pulled apart under deuteranopia — that is
 * inherent to traffic-light hues, not a bad pick — so severity is NEVER carried by
 * colour alone: every indicator also gets its own `glyph` shape and its text label,
 * and the four glyphs stay distinguishable in greyscale and in print.
 */

export const SEVERITY = {
  CRITICAL: { fill: "#8f1d14", ink: "#7d1d12", soft: "#f7e3df", glyph: "■", rank: 4 },
  HIGH: { fill: "#d13a2a", ink: "#a8301f", soft: "#fae7e2", glyph: "▲", rank: 3 },
  MEDIUM: { fill: "#b58200", ink: "#8a6508", soft: "#faeed3", glyph: "◆", rank: 2 },
  LOW: { fill: "#43976a", ink: "#2b6b47", soft: "#e3ede5", glyph: "●", rank: 1 },
  NONE: { fill: "#c4b8a2", ink: "#5c554a", soft: "#f1ece1", glyph: "·", rank: 0 },
};

/** Neutral fallback so an unknown level renders legibly instead of vanishing. */
const UNKNOWN = { fill: "#8a8175", ink: "#5c554a", soft: "#f1ece1", glyph: "·", rank: -1 };

export const sev = (level) => SEVERITY[String(level || "").toUpperCase()] || UNKNOWN;

export const sevFill = (level) => sev(level).fill;

/**
 * Where a signal sits on the evidence ladder. Not a severity — an *authority* —
 * so it deliberately does not reuse the traffic-light hues. We assert no official
 * rules anywhere in this system, so OFFICIAL_RULE is styled as the empty slot it is.
 */
export const AUTHORITY = {
  OFFICIAL_RULE: { ink: "#7f3520", soft: "#f6e6e0", label: "Official rule" },
  OBSERVED_BASELINE: { ink: "#8a6508", soft: "#faeed3", label: "Observed baseline" },
  STATISTICAL_OUTLIER: { ink: "#5c554a", soft: "#f1ece1", label: "Statistical outlier" },
};

export const authority = (key) =>
  AUTHORITY[key] || { ink: "#5c554a", soft: "#f1ece1", label: prettify(key) };

/**
 * Temporal classifications map onto the same scale by what they mean for a
 * reviewer: a sudden change is worth looking at, "stable" and "normal" are not.
 * These used to be terracotta — the alarm colour — for the two *reassuring* states.
 */
export const TREND_LEVEL = {
  NORMAL: "LOW",
  STABLE: "LOW",
  EMERGING: "MEDIUM",
  GROWING: "MEDIUM",
  DECLINING: "MEDIUM",
  PERSISTENT_CHANGE: "HIGH",
  SUDDEN_CHANGE: "CRITICAL",
  INSUFFICIENT_HISTORY: "NONE",
};

/** How alike two works are. Ordinal, so it rides the same ladder. */
export const DUPLICATE_LEVEL = {
  EXACT: "CRITICAL",
  NEAR_EXACT: "HIGH",
  HIGH_SIMILARITY: "MEDIUM",
  POSSIBLE_REPEAT: "LOW",
};

/**
 * A 0..1 score where **higher is better** — a health component, a completion rate.
 * Inverted against the severity ladder on purpose: a healthy score is green, a poor
 * one red. These meters used to be painted the alarm colour at every value, which
 * made a component scoring 95% look exactly as urgent as one scoring 5%.
 */
export function scoreFill(value) {
  if (value == null || Number.isNaN(value)) return SEVERITY.NONE.fill;
  if (value >= 0.75) return SEVERITY.LOW.fill;
  if (value >= 0.45) return SEVERITY.MEDIUM.fill;
  return SEVERITY.HIGH.fill;
}

/**
 * A 0..1 risk where **higher is worse** — completion risk, early-warning score.
 * The plain reading of the severity ladder.
 */
export function riskFill(value) {
  if (value == null || Number.isNaN(value)) return SEVERITY.NONE.fill;
  if (value >= 0.75) return SEVERITY.CRITICAL.fill;
  if (value >= 0.5) return SEVERITY.HIGH.fill;
  if (value >= 0.25) return SEVERITY.MEDIUM.fill;
  return SEVERITY.LOW.fill;
}

/** UPPER_SNAKE -> "Upper snake". Replaces every underscore, not just the first. */
export function prettify(key) {
  if (!key) return "—";
  const s = String(key).replace(/_/g, " ").toLowerCase();
  return s.charAt(0).toUpperCase() + s.slice(1);
}
