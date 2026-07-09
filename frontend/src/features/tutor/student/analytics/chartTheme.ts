/**
 * Chart palette for the student analytics page.
 *
 * Recharts renders SVG and needs concrete colour values, so these mirror the
 * Mira design tokens in `globals.css` as literal hex (kept in sync by hand).
 */
import type { Tone } from "@/lib/tones";
import type { Understanding } from "@/lib/tones";

export const CHART = {
  ink: "#232019",
  ink2: "#5e574b",
  ink3: "#94897a",
  line: "#e7ddcb",
  paper2: "#f4eddf",
  green: "#12805c",
  greenSoft: "#dceee3",
  coral: "#e9603c",
  coralSoft: "#fadfd5",
  amber: "#db960f",
  amberSoft: "#f7eac6",
  violet: "#6c57de",
  violetSoft: "#e8e3fb",
} as const;

/** Primary series colours: mastery reads as the "achieved" line, confidence as intent. */
export const MASTERY_COLOR = CHART.green;
export const CONFIDENCE_COLOR = CHART.violet;

export const toneColor: Record<Tone, string> = {
  green: CHART.green,
  violet: CHART.violet,
  amber: CHART.amber,
  coral: CHART.coral,
};

export const understandingColor: Record<Understanding, string> = {
  yes: CHART.green,
  partial: CHART.amber,
  no: CHART.coral,
};

/** Shared recharts style for the floating tooltip surface. */
export const TOOLTIP_STYLE = {
  borderRadius: 10,
  border: `1px solid ${CHART.line}`,
  background: "#ffffff",
  fontSize: 12,
  color: CHART.ink,
  boxShadow: "0 6px 20px rgba(35,32,25,0.08)",
} as const;

/** Shared recharts axis tick style. */
export const AXIS_TICK = { fontSize: 11, fill: CHART.ink3 } as const;

/** Categorical palette for misconception categories (cycled by index). */
export const CATEGORY_COLORS = [
  CHART.coral,
  CHART.amber,
  CHART.violet,
  CHART.green,
  CHART.ink3,
] as const;

/** Bar/point colour keyed off a 0–1 mastery score (mirrors `masteryFillClass`). */
export function masteryColor(mastery: number): string {
  if (mastery >= 0.66) return CHART.green;
  if (mastery >= 0.4) return CHART.amber;
  return CHART.coral;
}

/** Normalize an arbitrary tone string from the API onto a known Tone. */
export function safeTone(tone: string): Tone {
  return tone === "violet" || tone === "amber" || tone === "coral"
    ? tone
    : "green";
}
