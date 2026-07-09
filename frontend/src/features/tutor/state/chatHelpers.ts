import type {
  Chat,
  ChatMessage,
  ChatStatus,
  Control,
  MessageSender,
  MessageSpec,
} from "../types";
import type { SeededHistory } from "../data/seeds";

/** Live conversation state, folded back into `chats` on every navigation. */
export interface ChatEngineState {
  chats: Record<string, Chat>;
  order: string[];
  activeChatId: string | null;
  subjectId: string;
  status: ChatStatus;
  locked: boolean;
  title: string;
  messages: ChatMessage[];
  controls: Control[];
  typing: boolean;
  hintRung: number;
  leakChecks: number;
  nextId: number;
}

export function initialChatState(seeds: SeededHistory): ChatEngineState {
  return {
    chats: seeds.chats,
    order: seeds.order,
    activeChatId: null,
    subjectId: "fractions",
    status: "draft",
    locked: false,
    title: "",
    messages: [],
    controls: [],
    typing: false,
    hintRung: 0,
    leakChecks: 0,
    nextId: seeds.nextId,
  };
}

/** Turn message specs into id'd messages; quizzes are cloned per message. */
export function materialize(
  specs: MessageSpec[],
  from: MessageSender,
  startId: number,
): ChatMessage[] {
  return specs.map((spec, index) => ({
    id: startId + index,
    from,
    kind: spec.kind ?? "text",
    text: spec.text ?? "",
    diagnosis: spec.diagnosis,
    quiz: spec.quiz ? { ...spec.quiz } : undefined,
  }));
}

/** Fold the live conversation back into its stored chat record. */
export function commit(state: ChatEngineState): Record<string, Chat> {
  const id = state.activeChatId;
  const current = id ? state.chats[id] : undefined;
  if (!id || !current) return state.chats;
  return {
    ...state.chats,
    [id]: {
      ...current,
      messages: state.messages,
      controls: state.controls,
      hintRung: state.hintRung,
      leakChecks: state.leakChecks,
      status: state.status,
      title: state.title || current.title,
      subjectId: state.subjectId,
    },
  };
}

/** Replace one quiz message's data via an updater. */
export function patchQuiz(
  state: ChatEngineState,
  msgId: number,
  patch: (message: ChatMessage) => ChatMessage,
): ChatMessage[] {
  return state.messages.map((message) =>
    message.id === msgId && message.quiz ? patch(message) : message,
  );
}

/** Append a student message, registering the chat on its first question. */
export function appendMaya(
  state: ChatEngineState,
  text: string,
): ChatEngineState {
  const id = state.activeChatId;
  const registering = state.status === "draft" && id;
  const base = registering
    ? {
        chats: {
          ...state.chats,
          [id]: {
            id,
            subjectId: state.subjectId,
            title: text,
            status: "pending" as ChatStatus,
            messages: [],
            controls: [],
            hintRung: state.hintRung,
            leakChecks: state.leakChecks,
          },
        },
        order: [id, ...state.order.filter((x) => x !== id)],
        status: "pending" as ChatStatus,
        title: text,
      }
    : {};
  const [message] = materialize([{ text }], "maya", state.nextId);
  return {
    ...state,
    ...base,
    messages: [...state.messages, message!],
    controls: [],
    nextId: state.nextId + 1,
  };
}

/** Append the closing messages and lock the active chat as completed. */
export function finish(
  state: ChatEngineState,
  specs: MessageSpec[],
): ChatEngineState {
  const messages = [
    ...state.messages,
    ...materialize(specs, "tutor", state.nextId),
  ];
  const id = state.activeChatId;
  const current = id ? state.chats[id] : undefined;
  const chats =
    id && current
      ? {
          ...state.chats,
          [id]: {
            ...current,
            status: "completed" as ChatStatus,
            messages,
            controls: [],
          },
        }
      : state.chats;
  return {
    ...state,
    messages,
    chats,
    controls: [],
    typing: false,
    status: "completed",
    locked: true,
    nextId: state.nextId + specs.length,
  };
}
