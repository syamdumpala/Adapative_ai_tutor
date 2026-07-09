import type { Subject } from "../types";

/** The subject catalog shown on the student home screen. */
export const SUBJECTS: Subject[] = [
  {
    id: "fractions",
    name: "Fractions",
    glyph: "½",
    tone: "green",
    desc: "Compare, simplify, add & subtract",
    meta: "7 concepts",
    progress: 0.42,
  },
  {
    id: "decimals",
    name: "Decimals",
    glyph: ".5",
    tone: "violet",
    desc: "Place value, rounding & operations",
    meta: "6 concepts",
    progress: 0,
    isNew: true,
  },
  {
    id: "percentages",
    name: "Percentages",
    glyph: "%",
    tone: "amber",
    desc: "Of a whole, discount & markup",
    meta: "5 concepts",
    progress: 0,
  },
  {
    id: "integers",
    name: "Integers",
    glyph: "±",
    tone: "coral",
    desc: "Negatives & the number line",
    meta: "5 concepts",
    progress: 0,
  },
  {
    id: "geometry",
    name: "Geometry",
    glyph: "△",
    tone: "green",
    desc: "Angles, area & perimeter",
    meta: "8 concepts",
    progress: 0,
  },
  {
    id: "ratios",
    name: "Ratios & Rates",
    glyph: "a:b",
    tone: "violet",
    desc: "Compare, scale & unit rate",
    meta: "6 concepts",
    progress: 0,
  },
];

export function subjectById(id: string): Subject {
  return SUBJECTS.find((subject) => subject.id === id) ?? SUBJECTS[0]!;
}
