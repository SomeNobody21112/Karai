import { useCountUp, useReveal } from "../hooks.js";

const VARIANTS = { left: "reveal-left", scale: "reveal-scale", up: "reveal" };

/** Wrap anything to fade-and-lift it in when it scrolls into view. */
export function Reveal({
  children,
  variant = "up",
  delay = 0,
  as: Tag = "div",
  className = "",
  style,
  ...rest
}) {
  const [ref, visible] = useReveal();
  const base = VARIANTS[variant] || VARIANTS.up;
  return (
    <Tag
      ref={ref}
      className={[base, visible ? "in" : "", className].filter(Boolean).join(" ")}
      style={{ transitionDelay: `${delay}ms`, ...style }}
      {...rest}
    >
      {children}
    </Tag>
  );
}

/** A number that counts up the first time it scrolls into view. */
export function CountUp({
  end,
  format = (v) => v.toLocaleString("en-IN"),
  decimals = 0,
  duration,
}) {
  const [ref, visible] = useReveal({ threshold: 0.35 });
  const value = useCountUp(end, { active: visible, decimals, duration });
  return <span ref={ref}>{format(value)}</span>;
}
