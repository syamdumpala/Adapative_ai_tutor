import type { Control, DialogueStep, MessageSpec } from "../types";
import { quiz1 } from "./quizzes";
import { GENERIC_STEPS } from "./dialogueGeneric";

/** Diagnosis emitted when the student shows whole-number bias. */
export const DIAGNOSIS = {
  err: "conceptual",
  misc: "MISC-FR-01",
  name: "whole-number bias",
  prereq: "equal partitioning",
  quote: "“1/5 — 5 is bigger than 4”",
} as const;

const PROBE: Control[] = [
  { label: "1/5 — 5 is bigger than 4", key: "probe_wrong", variant: "primary" },
  { label: "1/4, I think", key: "probe_right", variant: "ghost" },
];

const AFTER_DIAGNOSIS: Control[] = [
  { label: "Okay, show me", key: "show_me", variant: "primary" },
  { label: "Just tell me the answer", key: "just_tell", variant: "ghost" },
];

const HINT_1: Control[] = [
  { label: "Hmm, still stuck", key: "still_stuck", variant: "ghost" },
  { label: "Each slice gets smaller!", key: "got_it_1", variant: "primary" },
];

const HINT_2: Control[] = [
  { label: "The half-slice is bigger!", key: "got_it_2", variant: "primary" },
  { label: "Show a worked example", key: "want_worked", variant: "ghost" },
];

// got_it_1 and got_it_2 converge on the same lock-in + first quiz.
const LOCK_IN: MessageSpec[] = [
  {
    text: "Yes! Exactly — fewer pieces, bigger slice. So 1/2 is a bigger slice than 1/3, and you rebuilt that yourself.",
  },
  {
    text: "Let’s lock it in with a couple of gentle ones. Tell me how sure you feel each time — that helps me help you.",
  },
  { kind: "quiz", quiz: quiz1() },
];

/** Suggested replies offered when a subject conversation first opens. */
export function starterControls(subjectId: string): Control[] {
  if (subjectId === "fractions") {
    return [
      {
        label: "Why is 1/2 bigger than 1/3?",
        key: "ask_canonical",
        variant: "primary",
      },
      {
        label: "Help me compare fraction sizes",
        key: "keep_going",
        variant: "ghost",
      },
    ];
  }
  return [
    { label: "Give me a warm-up", key: "g_warmup", variant: "primary" },
    { label: "Where should I start?", key: "g_start", variant: "ghost" },
  ];
}

// The scripted Fractions flow: diagnose → hint ladder → rebuild → quiz.
const FRACTIONS_STEPS: Record<string, DialogueStep> = {
  ask_canonical: {
    userText: "Why is 1/2 bigger than 1/3?",
    reply: [
      {
        text: "Great question — and I promise we’ll get there together. First, a quick check so I teach the right thing:",
      },
      {
        text: "Which is bigger, 1/4 or 1/5 — and what’s your gut say about why?",
      },
    ],
    controls: PROBE,
  },
  keep_going: {
    userText: "Help me compare fraction sizes",
    reply: [
      {
        text: "Happy to. Let’s start with the one that trips a lot of people up — which is bigger, 1/4 or 1/5, and why?",
      },
    ],
    controls: PROBE,
  },
  probe_right: {
    userText: "1/4, I think",
    reply: [
      {
        text: "Nice instinct! Let’s make sure it’s solid and not a lucky guess — one more: 1/3 vs 1/5, which wins, and why?",
      },
    ],
    controls: [
      { label: "1/5 — it has more", key: "probe_wrong", variant: "primary" },
    ],
  },
  probe_wrong: {
    userText: "1/5 — 5 is bigger than 4",
    delay: 950,
    reply: [
      {
        text: "Thank you — that’s a really common way to see it, and it tells me exactly where to help.",
      },
      { kind: "diagnosis", diagnosis: { ...DIAGNOSIS } },
      {
        text: "Here’s the thing: when the top number is 1, more pieces means each piece is smaller. Let’s rebuild that from how the pieces are made — I’ll show you.",
      },
    ],
    controls: AFTER_DIAGNOSIS,
  },
  just_tell: {
    userText: "Just tell me the answer",
    incLeak: true,
    setHintRung: 1,
    reply: [
      {
        text: "I could — but you’re closer than you think, and it means more when it’s yours. Here’s a nudge instead:",
      },
      {
        text: "The bottom number tells you how many equal pieces the whole is cut into. If a pizza is cut into more pieces, what happens to each slice?",
      },
    ],
    controls: HINT_1,
  },
  show_me: {
    incLeak: true,
    setHintRung: 1,
    reply: [
      {
        text: "Here’s a nudge to get us rolling: the bottom number is how many equal pieces the whole is cut into. Cut a pizza into more pieces — what happens to each slice?",
      },
    ],
    controls: HINT_1,
  },
  still_stuck: {
    userText: "Hmm, still stuck",
    incLeak: true,
    setHintRung: 2,
    delay: 950,
    reply: [
      { text: "No worries — let’s make it visual:" },
      { kind: "hintVisual" },
      {
        text: "Point to one single slice in each pizza. Which single slice is the bigger meal?",
      },
    ],
    controls: HINT_2,
  },
  want_worked: {
    incLeak: true,
    setHintRung: 3,
    delay: 900,
    reply: [
      {
        text: "Sure — here’s a similar one worked through, with different numbers so the thinking is what carries over:",
      },
      { kind: "worked" },
      {
        text: "See how fewer pieces made each piece bigger? Now try ours the same way.",
      },
    ],
    controls: [
      {
        label: "Oh! The half-slice is bigger",
        key: "got_it_2",
        variant: "primary",
      },
    ],
  },
  got_it_1: {
    userText: "Each slice gets smaller!",
    delay: 900,
    reply: LOCK_IN,
  },
  got_it_2: {
    userText: "The half-slice is bigger!",
    delay: 900,
    reply: LOCK_IN,
  },
};

/**
 * The guided conversation as data. Text supports `{name}` and `{subject}`
 * placeholders, interpolated by the chat engine at dispatch time. Quiz specs
 * are cloned per message when materialized, so sharing this constant is safe.
 */
export const DIALOGUE: Record<string, DialogueStep> = {
  ...FRACTIONS_STEPS,
  ...GENERIC_STEPS,
};
