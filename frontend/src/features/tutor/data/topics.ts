import type { Topic } from "../types";

/** The topic catalog shown on the student home screen. */
export const TOPICS: Topic[] = [
  {
    id: "1",
    name: "Fractions",
    glyph: "½",
    tone: "green",
    desc: "Compare, simplify, add & subtract",
    meta: "7 concepts",
    progress: 0.42,
  },
  {
    id: "2",
    name: "Decimals",
    glyph: ".5",
    tone: "violet",
    desc: "Place value, rounding & operations",
    meta: "6 concepts",
    progress: 0,
    isNew: true,
  },
  {
    id: "3",
    name: "Percentages",
    glyph: "%",
    tone: "amber",
    desc: "Of a whole, discount & markup",
    meta: "5 concepts",
    progress: 0,
  },
  {
    id: "4",
    name: "Integers",
    glyph: "±",
    tone: "coral",
    desc: "Negatives & the number line",
    meta: "5 concepts",
    progress: 0,
  },
  {
    id: "5",
    name: "Geometry",
    glyph: "△",
    tone: "green",
    desc: "Angles, area & perimeter",
    meta: "8 concepts",
    progress: 0,
  },
  {
    id: "6",
    name: "Ratios & Rates",
    glyph: "a:b",
    tone: "violet",
    desc: "Compare, scale & unit rate",
    meta: "6 concepts",
    progress: 0,
  },
];

export function topicById(id: string): Topic {
  return TOPICS.find((topic) => topic.id === id) ?? TOPICS[0]!;
}
