/**
 * The emblem: a chakra-derived seal over a ledger column.
 *
 * Reads as a government mark rather than a tech logo — a struck-seal ring with radial
 * spokes (public office), enclosing three ascending bars (the ledger being audited).
 * Drawn in currentColor so it inherits whatever surface it sits on.
 */
export default function Logo({ size = 36, className = "", title = "MPLADS Intelligence" }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      className={className}
      role="img"
      aria-label={title}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>{title}</title>
      {/* struck seal — outer ring */}
      <circle cx="24" cy="24" r="21.25" stroke="currentColor" strokeWidth="1.5" opacity="0.55" />
      <circle cx="24" cy="24" r="17.75" stroke="currentColor" strokeWidth="2.25" />

      {/* radial spokes at the cardinals — the chakra reference, kept restrained */}
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
        <line
          key={deg}
          x1="24"
          y1="3.4"
          x2="24"
          y2="6.6"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          opacity={deg % 90 === 0 ? 0.95 : 0.45}
          transform={`rotate(${deg} 24 24)`}
        />
      ))}

      {/* the ledger: three ascending bars on a baseline */}
      <path d="M15 32.5h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <rect x="16.25" y="24.5" width="4" height="6" rx="0.75" fill="currentColor" opacity="0.55" />
      <rect x="22" y="20.25" width="4" height="10.25" rx="0.75" fill="currentColor" opacity="0.8" />
      <rect x="27.75" y="15.5" width="4" height="15" rx="0.75" fill="currentColor" />
    </svg>
  );
}
