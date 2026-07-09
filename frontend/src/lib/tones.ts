/**
 * Semantic colour helpers for the Mira palette.
 *
 * Tailwind's JIT only sees *literal* class strings, so every tone maps to a
 * complete class name here rather than being built by concatenation at runtime
 * (`bg-${tone}-s` would be invisible to the compiler and get purged).
 */

/** Topic accent tone. */
export type Tone = "green" | "violet" | "amber" | "coral";

/** A learner's overall health, used for chips and avatar gradients. */
export type Health = "good" | "warn" | "bad";

/** How well a student grasped a topic. */
export type Understanding = "yes" | "partial" | "no";

/** Soft-tinted background + deep-ink text for a glyph tile. */
export const glyphTileTone: Record<Tone, string> = {
  green: "bg-green-s text-green-d",
  violet: "bg-violet-s text-violet-d",
  amber: "bg-amber-s text-amber",
  coral: "bg-coral-s text-coral-d",
};

/** Deep-ink text colour for a call-to-action label. */
export const ctaTextTone: Record<Tone, string> = {
  green: "text-green-d",
  violet: "text-violet-d",
  amber: "text-amber",
  coral: "text-coral-d",
};

/** Solid fill colour for a progress bar. */
export const progressFillTone: Record<Tone, string> = {
  green: "bg-green",
  violet: "bg-violet",
  amber: "bg-amber",
  coral: "bg-coral",
};

/** Status chip for a learner's health. */
export const healthChipTone: Record<Health, string> = {
  good: "bg-green-s text-green-d",
  warn: "bg-amber-s text-amber",
  bad: "bg-coral-s text-coral-d",
};

/** Chip + label for topic understanding. */
export const understandingChipTone: Record<Understanding, string> = {
  yes: "bg-green-s text-green-d",
  partial: "bg-amber-s text-amber",
  no: "bg-coral-s text-coral-d",
};

export const understandingLabel: Record<Understanding, string> = {
  yes: "Got it",
  partial: "Getting there",
  no: "Stuck",
};

/** Avatar / hero gradient background, as an inline `background` value. */
export type GradientTone = Health | "violet";

export const avatarGradient: Record<GradientTone, string> = {
  good: "linear-gradient(150deg, var(--color-green), var(--color-green-d))",
  warn: "linear-gradient(150deg, var(--color-amber), #b87908)",
  bad: "linear-gradient(150deg, var(--color-coral), var(--color-coral-d))",
  violet: "linear-gradient(150deg, var(--color-violet), var(--color-violet-d))",
};

/** Progress-bar fill colour keyed off a 0–1 mastery score. */
export function masteryFillClass(mastery: number): string {
  if (mastery >= 0.66) return "bg-green";
  if (mastery >= 0.4) return "bg-amber";
  return "bg-coral";
}

/** Text colour for a "+38%"-style improvement figure. */
export function improvementColorClass(improvement: string): string {
  const n = parseInt(improvement.replace(/[^0-9]/g, ""), 10) || 0;
  if (n >= 25) return "text-green-d";
  if (n >= 12) return "text-amber";
  return "text-coral-d";
}
