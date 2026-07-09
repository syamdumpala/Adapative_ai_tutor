import type { Tone } from "@/lib/tones";

export type Role = "student" | "teacher";
export type ChatStatus = "draft" | "pending" | "completed";
export type StudentScreen = "home" | "chat";
export type TeacherScreen = "home" | "topic" | "student";
export type ModalKind = "profile" | "performance" | null;

export type MessageSender = "maya" | "tutor";
export type MessageKind =
  "text" | "diagnosis" | "hintVisual" | "worked" | "quiz" | "revision";

export interface Subject {
  id: string;
  name: string;
  glyph: string;
  tone: Tone;
  desc: string;
  meta: string;
  /** Completion fraction, 0–1. */
  progress: number;
  isNew?: boolean;
}

export interface DiagnosisData {
  err: string;
  misc: string;
  name: string;
  prereq: string;
  quote: string;
}

export type ConfidenceValue = "sure" | "think" | "guess";

export interface QuizSegment {
  on: boolean;
  flex: number;
}

export interface QuizOption {
  type: "bar" | "label";
  correct: boolean;
  label?: string;
  segs?: QuizSegment[];
}

export interface QuizData {
  id: string;
  concept: string;
  diff: string;
  text: string;
  options: QuizOption[];
  confidence: ConfidenceValue | null;
  selected: number | null;
  answered: boolean;
  correct: boolean;
  needConf: boolean;
}

/** A single message, plus the structured payload its `kind` implies. */
export interface ChatMessage {
  id: number;
  from: MessageSender;
  kind: MessageKind;
  text: string;
  diagnosis?: DiagnosisData;
  quiz?: QuizData;
}

/** Input shape for a message the dialogue script wants to append. */
export interface MessageSpec {
  kind?: MessageKind;
  text?: string;
  diagnosis?: DiagnosisData;
  quiz?: QuizData;
}

export type ControlVariant = "primary" | "ghost";

export interface Control {
  label: string;
  key: string;
  variant: ControlVariant;
}

/** A branch of the guided conversation, keyed by control key. */
export interface DialogueStep {
  /** Optional student bubble appended immediately. */
  userText?: string;
  /** Tutor messages appended after `delay`. */
  reply: MessageSpec[];
  delay?: number;
  /** Suggested replies shown once the tutor finishes. */
  controls?: Control[];
  /** Set the hint-ladder rung (1–3) at dispatch time. */
  setHintRung?: number;
  /** Increment the "answer leak avoided" counter at dispatch time. */
  incLeak?: boolean;
}

export interface Chat {
  id: string;
  subjectId: string;
  title: string;
  status: ChatStatus;
  messages: ChatMessage[];
  controls: Control[];
  hintRung: number;
  leakChecks: number;
}
