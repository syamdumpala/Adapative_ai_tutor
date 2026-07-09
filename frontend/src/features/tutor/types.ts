import type { Tone } from "@/lib/tones";

export type Role = "student" | "teacher";
export type ChatStatus = "draft" | "pending" | "completed";
export type TeacherScreen = "home" | "topic" | "student" | "catalog";
export type ModalKind = "profile" | "performance" | null;

export type MessageSender = "maya" | "tutor";
export type MessageKind = "text";

export interface Topic {
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

/** A single conversation message. */
export interface ChatMessage {
  id: number;
  from: MessageSender;
  kind: MessageKind;
  text: string;
}
