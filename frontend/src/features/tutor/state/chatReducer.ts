import type { ConfidenceValue, Control, MessageSpec } from "../types";
import type { SeededHistory } from "../data/seeds";
import {
  type ChatEngineState,
  appendMaya,
  commit,
  finish,
  initialChatState,
  materialize,
  patchQuiz,
} from "./chatHelpers";

export type { ChatEngineState } from "./chatHelpers";
export { initialChatState } from "./chatHelpers";

export type ChatAction =
  | { type: "reset"; seeds: SeededHistory }
  | {
      type: "openSubject";
      subjectId: string;
      chatId: string;
      greeting: MessageSpec[];
      controls: Control[];
    }
  | { type: "openChat"; id: string }
  | { type: "goHome" }
  | { type: "commit" }
  | { type: "appendMaya"; text: string }
  | { type: "setTyping"; typing: boolean }
  | { type: "setHint"; rung: number }
  | { type: "incLeak" }
  | { type: "appendTutor"; specs: MessageSpec[] }
  | { type: "setControls"; controls: Control[] }
  | { type: "rateConf"; msgId: number; value: ConfidenceValue }
  | { type: "needConf"; msgId: number }
  | { type: "answerQuiz"; msgId: number; idx: number; correct: boolean }
  | { type: "retryQuiz"; msgId: number }
  | { type: "finish"; specs: MessageSpec[] };

type Handlers = {
  [K in ChatAction["type"]]: (
    state: ChatEngineState,
    action: Extract<ChatAction, { type: K }>,
  ) => ChatEngineState;
};

const HANDLERS: Handlers = {
  reset: (_state, action) => initialChatState(action.seeds),
  openSubject: (state, action) => ({
    ...state,
    chats: commit(state),
    activeChatId: action.chatId,
    subjectId: action.subjectId,
    status: "draft",
    locked: false,
    title: "",
    messages: materialize(action.greeting, "tutor", state.nextId),
    controls: action.controls,
    typing: false,
    hintRung: 0,
    leakChecks: 0,
    nextId: state.nextId + action.greeting.length,
  }),
  openChat: (state, action) => {
    const chats = commit(state);
    const chat = chats[action.id];
    if (!chat) return { ...state, chats };
    const locked = chat.status === "completed";
    return {
      ...state,
      chats,
      activeChatId: action.id,
      subjectId: chat.subjectId,
      status: chat.status,
      locked,
      title: chat.title,
      messages: chat.messages,
      controls: locked ? [] : chat.controls,
      typing: false,
      hintRung: chat.hintRung,
      leakChecks: chat.leakChecks,
    };
  },
  goHome: (state) => ({
    ...state,
    chats: commit(state),
    activeChatId: null,
    typing: false,
  }),
  commit: (state) => ({ ...state, chats: commit(state) }),
  appendMaya: (state, action) => appendMaya(state, action.text),
  setTyping: (state, action) => ({ ...state, typing: action.typing }),
  setHint: (state, action) => ({ ...state, hintRung: action.rung }),
  incLeak: (state) => ({ ...state, leakChecks: state.leakChecks + 1 }),
  appendTutor: (state, action) => ({
    ...state,
    typing: false,
    messages: [
      ...state.messages,
      ...materialize(action.specs, "tutor", state.nextId),
    ],
    nextId: state.nextId + action.specs.length,
  }),
  setControls: (state, action) => ({ ...state, controls: action.controls }),
  rateConf: (state, action) => ({
    ...state,
    messages: patchQuiz(state, action.msgId, (m) => ({
      ...m,
      quiz: { ...m.quiz!, confidence: action.value, needConf: false },
    })),
  }),
  needConf: (state, action) => ({
    ...state,
    messages: patchQuiz(state, action.msgId, (m) => ({
      ...m,
      quiz: { ...m.quiz!, needConf: true },
    })),
  }),
  answerQuiz: (state, action) => ({
    ...state,
    messages: patchQuiz(state, action.msgId, (m) => ({
      ...m,
      quiz: {
        ...m.quiz!,
        selected: action.idx,
        answered: true,
        correct: action.correct,
      },
    })),
  }),
  retryQuiz: (state, action) => ({
    ...state,
    messages: patchQuiz(state, action.msgId, (m) => ({
      ...m,
      quiz: { ...m.quiz!, answered: false, selected: null },
    })),
  }),
  finish: (state, action) => finish(state, action.specs),
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
