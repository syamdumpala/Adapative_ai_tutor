"use client";

import {
  type Dispatch,
  type MutableRefObject,
  useEffect,
  useReducer,
  useRef,
} from "react";
import {
  askTutor,
  fetchChatList,
  fetchChatMessages,
  toChatStatus,
} from "../api/chat";
import { type ChatEngineState, initialChatState } from "../state/chatHelpers";
import { type ChatAction, chatReducer } from "../state/chatReducer";

export interface MiraChat {
  state: ChatEngineState;
  openSubject: (subjectId: string) => void;
  openChat: (id: string) => void;
  goHome: () => void;
  sendMessage: (text: string) => void;
}

type Dispatcher = Dispatch<ChatAction>;

/** Open an existing conversation, loading its transcript from the backend. */
function runOpen(
  dispatch: Dispatcher,
  state: ChatEngineState,
  id: string,
): void {
  const summary = state.chats[id];
  if (!summary) return;
  dispatch({
    type: "openExisting",
    id,
    subjectId: summary.subjectId,
    title: summary.title,
    status: summary.status,
    hintRung: summary.hintRung,
    messages: [],
  });
  fetchChatMessages(id)
    .then((messages) => dispatch({ type: "setMessages", id, messages }))
    .catch(() => undefined);
}

/** Send one student turn to the live tutor graph and append its reply. */
async function runSend(
  dispatch: Dispatcher,
  sending: MutableRefObject<boolean>,
  state: ChatEngineState,
  text: string,
): Promise<void> {
  const trimmed = text.trim();
  if (!trimmed || sending.current) return;
  sending.current = true;
  dispatch({ type: "sendUser", text: trimmed });
  try {
    const res = await askTutor(trimmed, state.sessionId, state.subjectId);
    dispatch({
      type: "tutorReply",
      sessionId: res.session_id,
      text: res.message,
      status: toChatStatus(res.action),
      hintRung: res.hint_level ?? 0,
    });
  } catch (err) {
    const message =
      err instanceof Error
        ? err.message
        : "The tutor is unavailable right now.";
    dispatch({ type: "fail", message });
  } finally {
    sending.current = false;
  }
}

/** Live tutoring chat backed by `/tutor/sessions` (history) and `/tutor/ask`. */
export function useMiraChat(): MiraChat {
  const [state, dispatch] = useReducer(
    chatReducer,
    undefined,
    initialChatState,
  );
  const sending = useRef(false);

  useEffect(() => {
    let active = true;
    fetchChatList()
      .then(
        ({ chats, order }) =>
          active && dispatch({ type: "setList", chats, order }),
      )
      .catch(() => undefined);
    return () => {
      active = false;
    };
  }, []);

  return {
    state,
    openSubject: (subjectId) => dispatch({ type: "openDraft", subjectId }),
    openChat: (id) => runOpen(dispatch, state, id),
    goHome: () => dispatch({ type: "goHome" }),
    sendMessage: (text) => void runSend(dispatch, sending, state, text),
  };
}
