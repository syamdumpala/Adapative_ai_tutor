import type { ChatMessage, ChatStatus } from "../types";

/** A conversation as listed in the "Your chats" rail. */
export interface ChatSummary {
  id: string;
  subjectId: string;
  title: string;
  status: ChatStatus;
  hintRung: number;
}

/** Student chat state: the conversation list plus the open transcript. */
export interface ChatEngineState {
  chats: Record<string, ChatSummary>;
  order: string[];
  activeChatId: string | null; // null → home screen
  sessionId: string | null; // backend session id for the open chat
  subjectId: string;
  title: string;
  status: ChatStatus;
  locked: boolean; // completed conversations are read-only
  messages: ChatMessage[];
  typing: boolean;
  hintRung: number;
  tempId: number; // decrements to id optimistic messages before the server replies
  error: string | null;
}

/** Sentinel for a brand-new chat that has no backend session yet. */
export const NEW_CHAT = "__new__";

export function initialChatState(): ChatEngineState {
  return {
    chats: {},
    order: [],
    activeChatId: null,
    sessionId: null,
    subjectId: "fractions",
    title: "",
    status: "draft",
    locked: false,
    messages: [],
    typing: false,
    hintRung: 0,
    tempId: -1,
    error: null,
  };
}
