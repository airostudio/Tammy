// Minimal line-style icons matching the original site's design language -
// single stroke weight, no fill, replacing generic emoji markers.

type IconProps = { className?: string };

const base = "stroke-current fill-none";

export function CalendarIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className={`${base} ${className ?? ""}`}>
      <rect x="3.5" y="5" width="17" height="15.5" rx="2" />
      <path d="M3.5 9.5h17" />
      <path d="M8 3v4M16 3v4" />
    </svg>
  );
}

export function CheckCircleIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className={`${base} ${className ?? ""}`}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M8.5 12.5l2.4 2.4L16 9.5" />
    </svg>
  );
}

export function UsersIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className={`${base} ${className ?? ""}`}>
      <circle cx="9" cy="8.5" r="3" />
      <path d="M3.5 19c0-3.3 2.5-5.5 5.5-5.5s5.5 2.2 5.5 5.5" />
      <circle cx="17" cy="8" r="2.2" />
      <path d="M15.8 13.6c2.4.4 4.2 2.3 4.2 5" />
    </svg>
  );
}

export function DoorIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className={`${base} ${className ?? ""}`}>
      <path d="M6 21V4.6c0-.6.5-1 1.1-.9l9 1.6c.5.1.9.5.9 1V21" />
      <path d="M4 21h16" />
      <circle cx="13.5" cy="13" r="0.9" className="fill-current stroke-none" />
    </svg>
  );
}

export function MailIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className={`${base} ${className ?? ""}`}>
      <rect x="3.5" y="5.5" width="17" height="13" rx="2" />
      <path d="M4 6.5l8 6.5 8-6.5" />
    </svg>
  );
}

export function SparkleIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={`fill-current stroke-none ${className ?? ""}`}>
      <path d="M12 3c.4 3.3 1 4.7 2.2 5.9 1.2 1.2 2.6 1.8 5.9 2.2-3.3.4-4.7 1-5.9 2.2-1.2 1.2-1.8 2.6-2.2 5.9-.4-3.3-1-4.7-2.2-5.9-1.2-1.2-2.6-1.8-5.9-2.2 3.3-.4 4.7-1 5.9-2.2 1.2-1.2 1.8-2.6 2.2-5.9z" />
    </svg>
  );
}

export function CheckIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className={`${base} ${className ?? ""}`}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M8.5 12.5l2.4 2.4L16 9.5" />
    </svg>
  );
}

export function ClockIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className={`${base} ${className ?? ""}`}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.2 1.8" />
    </svg>
  );
}

export function ShieldIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className={`${base} ${className ?? ""}`}>
      <rect x="4" y="10" width="16" height="10" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  );
}
