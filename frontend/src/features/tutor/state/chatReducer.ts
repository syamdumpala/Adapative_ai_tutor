import type { ChatMessage, ChatStatus } from "../types";
import {
  type ChatEngineState,
  type ChatSummary,
  NEW_CHAT,
} from "./chatHelpers";

export type { ChatEngineState } from "./chatHelpers";

export type ChatAction =
  | { type: "setList"; chats: Record<string, ChatSummary>; order: string[] }
  | { type: "openDraft"; topicId: string }
  | {
      type: "openExisting";
      id: string;
      topicId: string;
      title: string;
      status: ChatStatus;
      hintRung: number;
      messages: ChatMessage[];
    }
  | { type: "setMessages"; id: string; messages: ChatMessage[] }
  | { type: "goHome" }
  | { type: "sendUser"; text: string }
  | {
      type: "tutorReply";
      sessionId: string;
      text: string;
      status: ChatStatus;
      hintRung: number;
    }
  | { type: "fail"; message: string };

function userMessage(state: ChatEngineState, text: string): ChatMessage {
  return { id: state.tempId, from: "maya", kind: "text", text };
}

// A one-off, client-only welcome shown when a fresh chat is opened. It is purely
// a UX touch — never sent to or stored by the backend.
const GREETING =
  "Hi! What would you like to work on today? Ask me anything about this topic — I'll guide you with hints, not just the answer.";

function greetingMessage(): ChatMessage {
  return { id: 0, from: "tutor", kind: "text", text: GREETING };
}

type Handlers = {
  [K in ChatAction["type"]]: (
    state: ChatEngineState,
    action: Extract<ChatAction, { type: K }>,
  ) => ChatEngineState;
};

const HANDLERS: Handlers = {
  setList: (state, action) => ({
    ...state,
    chats: action.chats,
    order: action.order,
  }),
  openDraft: (state, action) => ({
    ...state,
    activeChatId: NEW_CHAT,
    sessionId: null,
    topicId: action.topicId,
    title: "",
    status: "draft",
    locked: false,
    messages: [greetingMessage()],
    typing: false,
    hintRung: 0,
    error: null,
  }),
  openExisting: (state, action) => ({
    ...state,
    activeChatId: action.id,
    sessionId: action.id,
    topicId: action.topicId,
    title: action.title,
    status: action.status,
    locked: action.status === "completed",
    messages: action.messages,
    typing: false,
    hintRung: action.hintRung,
    error: null,
  }),
  setMessages: (state, action) =>
    state.activeChatId === action.id
      ? { ...state, messages: action.messages }
      : state,
  goHome: (state) => ({
    ...state,
    activeChatId: null,
    typing: false,
    error: null,
  }),
  sendUser: (state, action) => {
    const draft = state.status === "draft";
    return {
      ...state,
      messages: [...state.messages, userMessage(state, action.text)],
      typing: true,
      error: null,
      tempId: state.tempId - 1,
      status: draft ? "pending" : state.status,
      title: draft ? action.text.slice(0, 80) : state.title,
    };
  },
  tutorReply: (state, action) => {
    const id = action.sessionId;
    const summary: ChatSummary = {
      id,
      topicId: state.topicId,
      title: state.title || "New chat",
      status: action.status,
      hintRung: action.hintRung,
    };
    const reply: ChatMessage = {
      id: state.tempId,
      from: "tutor",
      kind: "text",
      text: action.text,
    };
    return {
      ...state,
      sessionId: id,
      activeChatId: id,
      messages: [...state.messages, reply],
      typing: false,
      hintRung: action.hintRung,
      status: action.status,
      locked: action.status === "completed",
      tempId: state.tempId - 1,
      chats: { ...state.chats, [id]: summary },
      order: [id, ...state.order.filter((x) => x !== id)],
    };
  },
  fail: (state, action) => ({ ...state, typing: false, error: action.message }),
};

export function chatReducer(
  state: ChatEngineState,
  action: ChatAction,
): ChatEngineState {
  const handler = HANDLERS[action.type] as (
    s: ChatEngineState,
    a: ChatAction,
  ) => ChatEngineState;
  return handler(state, action);
}
