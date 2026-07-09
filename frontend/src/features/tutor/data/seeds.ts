import type { Chat, ChatMessage, MessageSender } from "../types";

export interface SeededHistory {
  chats: Record<string, Chat>;
  order: string[];
  /** Next free message id after the seeds are laid down. */
  nextId: number;
}

interface SeedLine {
  from: MessageSender;
  text: string;
}

interface SeedChat {
  id: string;
  subjectId: string;
  title: string;
  status: Chat["status"];
  hintRung: number;
  leakChecks: number;
  lines: SeedLine[];
}

const SEED_CHATS: SeedChat[] = [
  {
    id: "seed_f1",
    subjectId: "fractions",
    title: "Comparing 1/2 and 1/3",
    status: "completed",
    hintRung: 0,
    leakChecks: 2,
    lines: [
      { from: "maya", text: "Why is 1/2 bigger than 1/3?" },
      {
        from: "tutor",
        text: "Good question! A bigger bottom number means more pieces, so each piece is smaller. Cut a pizza into 3 and each slice is smaller than cutting it into 2.",
      },
      { from: "maya", text: "Ohh, so 1/2 is the bigger slice." },
      {
        from: "tutor",
        text: "Exactly — you rebuilt that yourself. Lovely work today!",
      },
    ],
  },
  {
    id: "seed_p1",
    subjectId: "percentages",
    title: "What is 25% of 80?",
    status: "pending",
    hintRung: 1,
    leakChecks: 1,
    lines: [
      { from: "maya", text: "What is 25% of 80?" },
      {
        from: "tutor",
        text: "Let’s reason it out rather than jump to the answer. 25% is the same as one quarter — so what would you do to 80 to split it into four equal parts?",
      },
    ],
  },
  {
    id: "seed_d1",
    subjectId: "decimals",
    title: "Rounding 3.47 to tenths",
    status: "completed",
    hintRung: 0,
    leakChecks: 1,
    lines: [
      { from: "maya", text: "How do I round 3.47 to the nearest tenth?" },
      {
        from: "tutor",
        text: "Look at the digit just after the tenths place — the 7. Since 7 is 5 or more, the tenths digit rounds up, so 3.47 becomes 3.5. Nicely done!",
      },
    ],
  },
];

/** Fresh copy of the demo's seeded chat history. */
export function buildSeeds(): SeededHistory {
  const chats: Record<string, Chat> = {};
  const order: string[] = [];
  let id = 0;

  for (const seed of SEED_CHATS) {
    const messages: ChatMessage[] = seed.lines.map((line) => ({
      id: (id += 1),
      from: line.from,
      kind: "text",
      text: line.text,
    }));
    chats[seed.id] = {
      id: seed.id,
      subjectId: seed.subjectId,
      title: seed.title,
      status: seed.status,
      messages,
      controls: [],
      hintRung: seed.hintRung,
      leakChecks: seed.leakChecks,
    };
    order.push(seed.id);
  }

  return { chats, order, nextId: id + 1 };
}
