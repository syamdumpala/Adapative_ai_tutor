import { cn } from "@/lib/cn";
import type { ChatMessage, ConfidenceValue } from "../../types";
import { DiagnosisCard } from "./DiagnosisCard";
import { QuizCard } from "./QuizCard";
import { RevisionPlan } from "./RevisionPlan";
import { TutorMark } from "./TutorMark";
import { VisualHint } from "./VisualHint";
import { WorkedExample } from "./WorkedExample";

interface MessageRowProps {
  message: ChatMessage;
  celebrate: boolean;
  onRate: (msgId: number, value: ConfidenceValue) => void;
  onAnswer: (msgId: number, idx: number) => void;
}

function MessageContent({
  message,
  celebrate,
  onRate,
  onAnswer,
}: MessageRowProps) {
  switch (message.kind) {
    case "diagnosis":
      return message.diagnosis ? (
        <DiagnosisCard data={message.diagnosis} />
      ) : null;
    case "hintVisual":
      return <VisualHint />;
    case "worked":
      return <WorkedExample />;
    case "revision":
      return <RevisionPlan />;
    case "quiz":
      return message.quiz ? (
        <QuizCard
          quiz={message.quiz}
          celebrate={celebrate}
          onRate={(value) => onRate(message.id, value)}
          onAnswer={(idx) => onAnswer(message.id, idx)}
        />
      ) : null;
    default:
      return <div className="leading-[1.5]">{message.text}</div>;
  }
}

function bubbleClass(message: ChatMessage): string {
  if (message.from === "maya") {
    return "max-w-[82%] rounded-[16px_16px_5px_16px] bg-ink px-4 py-3 text-[14px] leading-[1.5] text-paper shadow-soft";
  }
  const base =
    "rounded-[16px_16px_16px_5px] border border-line bg-card px-4 py-[14px] text-ink shadow-soft";
  return message.kind === "text"
    ? cn(base, "max-w-[82%] text-[14px]")
    : cn(base, "w-full max-w-[520px]");
}

/** One conversation row: tutor mark + bubble, or a right-aligned student bubble. */
export function MessageRow({
  message,
  celebrate,
  onRate,
  onAnswer,
}: MessageRowProps) {
  const isMaya = message.from === "maya";
  return (
    <div
      className={cn(
        "flex max-w-full animate-msg-in items-end gap-[10px]",
        isMaya && "flex-row-reverse",
      )}
    >
      {!isMaya && <TutorMark />}
      <div className={bubbleClass(message)}>
        <MessageContent
          message={message}
          celebrate={celebrate}
          onRate={onRate}
          onAnswer={onAnswer}
        />
      </div>
    </div>
  );
}
