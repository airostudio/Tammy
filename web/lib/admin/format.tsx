const MUTED_STATUSES = new Set(["completed", "checked_out", "archived", "cancelled", "read"]);
const WARNING_STATUSES = new Set(["no_show", "urgent", "flagged"]);

export function formatDateTime(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (isNaN(date.getTime())) return value;
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function Pill({ value }: { value?: string | null }) {
  if (!value) return null;
  const tone = MUTED_STATUSES.has(value) ? "muted" : WARNING_STATUSES.has(value) ? "warning" : "default";
  const toneClasses =
    tone === "muted"
      ? "bg-surface-sunken text-ink-faint"
      : tone === "warning"
        ? "bg-brass-tint text-brass"
        : "bg-teal-tint text-teal-deep";

  return (
    <span className={`inline-block rounded-full px-3 py-1 text-[12.5px] font-semibold whitespace-nowrap ${toneClasses}`}>
      {value.replace(/_/g, " ")}
    </span>
  );
}
