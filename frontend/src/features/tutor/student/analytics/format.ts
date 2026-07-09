/** Small formatting helpers shared across the analytics charts. */

/** ISO timestamp → "12 Jul" (falls back to a short session label). */
export function shortDate(iso: string | null, fallback = ""): string {
  if (!iso) return fallback;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return fallback;
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

/** 0–1 score → whole-percent string, e.g. 0.72 → "72%". */
export function pct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

/** 0–1 score → whole percent number, e.g. 0.72 → 72. */
export function toPct(value: number): number {
  return Math.round(value * 100);
}

/** Truncate a label so axis ticks stay readable. */
export function clip(text: string, max = 16): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}
