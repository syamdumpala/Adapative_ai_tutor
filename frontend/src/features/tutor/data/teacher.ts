import type { Health, Understanding } from "@/lib/tones";
import { fullName, initialsOf } from "./student";

export interface TeacherTopic {
  id: string;
  name: string;
  glyph: string;
  /** `bg-* text-*` classes for the topic's glyph tile. */
  tile: string;
  short: string;
  long: string;
}

export interface Engagement {
  asked: number;
  u: Understanding;
  /** Mastery score, 0–1. */
  m: number;
}

export interface TeacherStudent {
  id: string;
  name: string;
  initials: string;
  tone: Health;
  status: string;
  improvement: string;
  eng: Record<string, Engagement>;
}

export interface TopicAggregate {
  students: number;
  questions: number;
  understood: number;
}

export const TEACHER_TOPICS: TeacherTopic[] = [
  {
    id: "partition",
    name: "Equal partitioning",
    glyph: "◐",
    tile: "bg-green-s text-green-d",
    short: "Splitting a whole into equal-sized parts.",
    long: "Every fraction starts here: a whole cut into parts that are exactly the same size. Students who are shaky on equal partitioning tend to miscount pieces and misread what the bottom number means.",
  },
  {
    id: "unit",
    name: "Unit fractions & part–whole",
    glyph: "½",
    tile: "bg-violet-s text-violet-d",
    short: "Reading 1/n as one of n equal parts.",
    long: "Understanding that 1/n names a single part when a whole is split into n equal parts — the bridge between partitioning and naming fractions.",
  },
  {
    id: "cmpUnit",
    name: "Comparing unit fractions",
    glyph: "⅕",
    tile: "bg-amber-s text-amber",
    short: "Why 1/5 is smaller than 1/4.",
    long: "More pieces means smaller pieces. This is where whole-number bias shows up most — students assume 1/5 > 1/4 because 5 > 4.",
  },
  {
    id: "cmpAny",
    name: "Comparing any fractions",
    glyph: "⅗",
    tile: "bg-coral-s text-coral-d",
    short: "Ordering fractions with different tops and bottoms.",
    long: "Comparing fractions that differ in both numerator and denominator using benchmarks, common denominators, or equivalent forms.",
  },
  {
    id: "equiv",
    name: "Equivalent fractions",
    glyph: "=",
    tile: "bg-green-s2 text-green-d",
    short: "Different fractions naming the same amount.",
    long: "Recognizing that 1/2, 2/4 and 3/6 all name the same quantity — the foundation for adding unlike denominators later.",
  },
  {
    id: "addLike",
    name: "Adding like denominators",
    glyph: "+",
    tile: "bg-paper2 text-ink",
    short: "Combining fractions that share a denominator.",
    long: "Adding and subtracting fractions when the bottom numbers already match — count the pieces, keep the denominator.",
  },
];

export function topicById(id: string | null): TeacherTopic {
  return TEACHER_TOPICS.find((topic) => topic.id === id) ?? TEACHER_TOPICS[0]!;
}

// The demo student ("Maya") — name/initials are supplied at build time.
const MAYA: Omit<TeacherStudent, "name" | "initials"> = {
  id: "maya",
  tone: "good",
  status: "Improving",
  improvement: "+38%",
  eng: {
    partition: { asked: 3, u: "yes", m: 0.7 },
    cmpUnit: { asked: 2, u: "yes", m: 0.6 },
    cmpAny: { asked: 2, u: "yes", m: 0.6 },
    equiv: { asked: 1, u: "partial", m: 0.3 },
  },
};

const OTHER_STUDENTS: TeacherStudent[] = [
  {
    id: "priya",
    name: "Priya Nair",
    initials: "PN",
    tone: "good",
    status: "Steady",
    improvement: "+24%",
    eng: {
      partition: { asked: 1, u: "yes", m: 0.82 },
      cmpAny: { asked: 2, u: "yes", m: 0.71 },
      equiv: { asked: 2, u: "yes", m: 0.58 },
    },
  },
  {
    id: "leo",
    name: "Leo Meyer",
    initials: "LM",
    tone: "good",
    status: "Steady",
    improvement: "+18%",
    eng: {
      partition: { asked: 1, u: "yes", m: 0.74 },
      unit: { asked: 1, u: "partial", m: 0.55 },
      cmpAny: { asked: 1, u: "yes", m: 0.66 },
    },
  },
  {
    id: "sam",
    name: "Sam Ortiz",
    initials: "SO",
    tone: "warn",
    status: "Watch",
    improvement: "+12%",
    eng: {
      partition: { asked: 2, u: "partial", m: 0.52 },
      cmpAny: { asked: 1, u: "no", m: 0.4 },
      equiv: { asked: 1, u: "no", m: 0.28 },
    },
  },
  {
    id: "rohan",
    name: "Rohan Das",
    initials: "RD",
    tone: "bad",
    status: "At risk",
    improvement: "+6%",
    eng: {
      partition: { asked: 1, u: "partial", m: 0.3 },
      cmpAny: { asked: 4, u: "no", m: 0.15 },
    },
  },
];

/** Build the class roster; the demo student's row uses the configured name. */
export function buildStudents(studentName: string): TeacherStudent[] {
  const maya = {
    ...MAYA,
    name: fullName(studentName),
    initials: initialsOf(studentName),
  };
  return [maya, ...OTHER_STUDENTS];
}

export function studentById(
  students: TeacherStudent[],
  id: string,
): TeacherStudent {
  return students.find((student) => student.id === id) ?? students[0]!;
}

/** Aggregate engagement for one topic across the roster. */
export function topicAggregate(
  students: TeacherStudent[],
  topicId: string,
): TopicAggregate {
  let asked = 0;
  let questions = 0;
  let understood = 0;
  for (const student of students) {
    const engagement = student.eng[topicId];
    if (!engagement) continue;
    asked += 1;
    questions += engagement.asked;
    if (engagement.u === "yes") understood += 1;
  }
  return { students: asked, questions, understood };
}
