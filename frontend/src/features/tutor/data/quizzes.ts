import type { QuizData } from "../types";

const BLANK = {
  confidence: null,
  selected: null,
  answered: false,
  correct: false,
  needConf: false,
} as const;

/** "Which bar shows 1/3 in equal pieces?" — segmented-bar options. */
export function quiz1(): QuizData {
  return {
    id: "q1",
    concept: "Equal partitioning",
    diff: "Easy",
    text: "Which bar shows 1/3 shaded — in equal pieces?",
    options: [
      {
        type: "bar",
        correct: true,
        segs: [
          { on: true, flex: 1 },
          { on: false, flex: 1 },
          { on: false, flex: 1 },
        ],
      },
      {
        type: "bar",
        correct: false,
        segs: [
          { on: true, flex: 1.8 },
          { on: false, flex: 0.6 },
          { on: false, flex: 0.6 },
        ],
      },
      {
        type: "bar",
        correct: false,
        segs: [
          { on: true, flex: 1 },
          { on: false, flex: 1 },
          { on: false, flex: 1 },
          { on: false, flex: 1 },
        ],
      },
    ],
    ...BLANK,
  };
}

/** "Which is the bigger slice — 1/3 or 1/5?" — text-label options. */
export function quiz2(): QuizData {
  return {
    id: "q2",
    concept: "Comparing unit fractions",
    diff: "Easy",
    text: "Which is the bigger slice — 1/3 or 1/5?",
    options: [
      { type: "label", correct: true, label: "1/3" },
      { type: "label", correct: false, label: "1/5" },
      { type: "label", correct: false, label: "They're equal" },
    ],
    ...BLANK,
  };
}
