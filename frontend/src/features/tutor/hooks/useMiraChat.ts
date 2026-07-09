"use client";

import { useEffect, useReducer, useRef } from "react";
import { buildSeeds } from "../data/seeds";
import { subjectById } from "../data/subjects";
import {
  type ChatEngineState,
  chatReducer,
  initialChatState,
} from "../state/chatReducer";
import type { ConfidenceValue } from "../types";
import {
  type Ctx,
  clearTimer,
  handleAnswer,
  openSubjectAction,
  runControl,
} from "./chatActions";

export interface MiraChat {
  state: ChatEngineState;
  openSubject: (subjectId: string) => void;
  openChat: (id: string) => void;
  goHome: () => void;
  commit: () => void;
  restart: () => void;
  sendControl: (key: string) => void;
  sendMessage: (text: string) => void;
  rateConfidence: (msgId: number, value: ConfidenceValue) => void;
  answerQuiz: (msgId: number, idx: number) => void;
}

/** The guided-conversation engine for one student session. */
export function useMiraChat(name: string): MiraChat {
  const [state, dispatch] = useReducer(chatReducer, null, () =>
    initialChatState(buildSeeds()),
  );
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const seq = useRef(0);
  const ctx: Ctx = { dispatch, timer };

  useEffect(() => () => clearTimer(timer), []);

  const subjectName = subjectById(state.subjectId).name;

  return {
    state,
    openSubject: (subjectId) => openSubjectAction(ctx, seq, name, subjectId),
    openChat: (id) => {
      clearTimer(timer);
      dispatch({ type: "openChat", id });
    },
    goHome: () => {
      clearTimer(timer);
      dispatch({ type: "goHome" });
    },
    commit: () => dispatch({ type: "commit" }),
    restart: () => {
      clearTimer(timer);
      dispatch({ type: "reset", seeds: buildSeeds() });
    },
    sendControl: (key) => runControl(ctx, key, name, subjectName),
    sendMessage: (text) => {
      if (text.trim()) dispatch({ type: "appendMaya", text: text.trim() });
    },
    rateConfidence: (msgId, value) =>
      dispatch({ type: "rateConf", msgId, value }),
    answerQuiz: (msgId, idx) => handleAnswer(ctx, state, { msgId, idx, name }),
  };
}
