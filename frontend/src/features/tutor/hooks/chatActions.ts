import type { Dispatch, MutableRefObject } from "react";
import { DIALOGUE, starterControls } from "../data/dialogue";
import { quiz2 } from "../data/quizzes";
import { subjectById } from "../data/subjects";
import type { ChatAction, ChatEngineState } from "../state/chatReducer";
import type { MessageSpec, QuizData } from "../types";

export type TimerRef = MutableRefObject<ReturnType<typeof setTimeout> | null>;
type Dispatcher = Dispatch<ChatAction>;

/** Everything the async dialogue helpers need to drive the reducer. */
export interface Ctx {
  dispatch: Dispatcher;
  timer: TimerRef;
}

export interface AnswerPayload {
  msgId: number;
  idx: number;
  name: string;
}

export function clearTimer(timer: TimerRef): void {
  if (timer.current) clearTimeout(timer.current);
}

function interpolate(text: string, name: string, subject: string): string {
  return text.replaceAll("{name}", name).replaceAll("{subject}", subject);
}

function interpolateSpec(
  spec: MessageSpec,
  name: string,
  subject: string,
): MessageSpec {
  return spec.text
    ? { ...spec, text: interpolate(spec.text, name, subject) }
    : spec;
}

function greetingText(name: string, subject: string): string {
  return `Hi ${name}! What would you like to work on in ${subject} today? Ask me anything, or tap a starter below.`;
}

function finishSpecs(name: string): MessageSpec[] {
  return [
    {
      text: "That’s two in a row with real confidence — beautiful. You went from “bigger number wins” to actually seeing the pieces.",
    },
    { kind: "revision" },
    {
      text: `Nice work today, ${name}. This chat is all wrapped up — I’ll check in on it again in a couple of days.`,
    },
  ];
}

export function openSubjectAction(
  ctx: Ctx,
  seq: MutableRefObject<number>,
  name: string,
  subjectId: string,
): void {
  clearTimer(ctx.timer);
  seq.current += 1;
  ctx.dispatch({
    type: "openSubject",
    subjectId,
    chatId: `c${seq.current}`,
    greeting: [{ text: greetingText(name, subjectById(subjectId).name) }],
    controls: starterControls(subjectId),
  });
}

export function runControl(
  ctx: Ctx,
  key: string,
  name: string,
  subject: string,
): void {
  const step = DIALOGUE[key];
  if (!step) return;
  clearTimer(ctx.timer);
  if (step.userText)
    ctx.dispatch({
      type: "appendMaya",
      text: interpolate(step.userText, name, subject),
    });
  if (step.incLeak) ctx.dispatch({ type: "incLeak" });
  if (step.setHintRung !== undefined)
    ctx.dispatch({ type: "setHint", rung: step.setHintRung });
  ctx.dispatch({ type: "setTyping", typing: true });
  const specs = step.reply.map((spec) => interpolateSpec(spec, name, subject));
  ctx.timer.current = setTimeout(() => {
    ctx.dispatch({ type: "appendTutor", specs });
    if (step.controls)
      ctx.dispatch({ type: "setControls", controls: step.controls });
  }, step.delay ?? 750);
}

function scheduleFinish(ctx: Ctx, name: string): void {
  ctx.timer.current = setTimeout(() => {
    ctx.dispatch({
      type: "appendTutor",
      specs: [
        {
          text: "And with real confidence, too — that’s the misconception melting away.",
        },
      ],
    });
    ctx.dispatch({ type: "setTyping", typing: true });
    ctx.timer.current = setTimeout(
      () => ctx.dispatch({ type: "finish", specs: finishSpecs(name) }),
      900,
    );
  }, 750);
}

function runAnswer(ctx: Ctx, quiz: QuizData, payload: AnswerPayload): void {
  const { msgId, idx, name } = payload;
  const correct = Boolean(quiz.options[idx]?.correct);
  ctx.dispatch({ type: "answerQuiz", msgId, idx, correct });
  clearTimer(ctx.timer);
  if (!correct) {
    ctx.timer.current = setTimeout(() => {
      ctx.dispatch({
        type: "appendTutor",
        specs: [
          {
            text: "Close — let’s look again, no stress. Count the pieces and check they’re all the same size.",
          },
        ],
      });
      ctx.dispatch({ type: "retryQuiz", msgId });
    }, 750);
    return;
  }
  if (quiz.id === "q1") {
    ctx.timer.current = setTimeout(() => {
      ctx.dispatch({
        type: "appendTutor",
        specs: [
          {
            text: "Nice — equal pieces, and you spotted it. That’s the whole game.",
          },
          { kind: "quiz", quiz: quiz2() },
        ],
      });
    }, 850);
    return;
  }
  scheduleFinish(ctx, name);
}

export function handleAnswer(
  ctx: Ctx,
  state: ChatEngineState,
  payload: AnswerPayload,
): void {
  const quiz = state.messages.find(
    (message) => message.id === payload.msgId,
  )?.quiz;
  if (!quiz || quiz.answered) return;
  if (!quiz.confidence) {
    ctx.dispatch({ type: "needConf", msgId: payload.msgId });
    return;
  }
  runAnswer(ctx, quiz, payload);
}
