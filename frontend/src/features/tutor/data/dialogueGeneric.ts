import type { DialogueStep, MessageSpec } from "../types";

// Shared reply for both "new to this" and "seen some" branches.
const INTRO: MessageSpec[] = [
  {
    text: "Perfect — that tells me where to begin. We’ll take it a step at a time, and I’ll remember how it goes so next time we pick up right here.",
  },
  {
    text: "Heads up: for this preview the fully adaptive flow — diagnosis, the hint ladder and memory — is wired on Fractions. Tap ‹ back and open Fractions to see it in action.",
  },
];

/** Warm-up flow for the non-Fractions subjects (adaptive demo lives on Fractions). */
export const GENERIC_STEPS: Record<string, DialogueStep> = {
  g_warmup: {
    userText: "Give me a warm-up",
    reply: [
      {
        text: "Love the energy. Quick gut-check first: with {subject}, do you feel new-to-this or like you’ve seen some of it?",
      },
    ],
    controls: [
      { label: "Pretty new to me", key: "g_new", variant: "primary" },
      { label: "I’ve seen some", key: "g_some", variant: "ghost" },
    ],
  },
  g_start: {
    userText: "Where should I start?",
    reply: [
      {
        text: "Great question. I’ll ask two or three quick check-questions first, then we skip what you’ve already got and spend time where it counts.",
      },
      { text: "Sound good?" },
    ],
    controls: [
      { label: "Sounds good, let’s go", key: "g_ready", variant: "primary" },
    ],
  },
  g_new: { userText: "Pretty new to me", delay: 650, reply: INTRO },
  g_some: { userText: "I’ve seen some", delay: 650, reply: INTRO },
  g_ready: {
    userText: "Sounds good, let’s go",
    delay: 650,
    reply: [
      {
        text: "Awesome. In this preview, the complete adaptive demo lives on Fractions — head back and pick Fractions to watch the diagnosis, hints and memory come together.",
      },
    ],
  },
};
