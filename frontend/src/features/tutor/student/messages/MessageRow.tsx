import { cn } from "@/lib/cn";
import type { ChatMessage } from "../../types";
import { TutorMark } from "./TutorMark";

interface MessageRowProps {
  message: ChatMessage;
}

function bubbleClass(isMaya: boolean): string {
  if (isMaya) {
    return "max-w-[82%] rounded-[16px_16px_5px_16px] bg-ink px-4 py-3 text-[14px] leading-[1.5] text-paper shadow-soft";
  }
  return "max-w-[82%] rounded-[16px_16px_16px_5px] border border-line bg-card px-4 py-[14px] text-[14px] text-ink shadow-soft";
}

/** One conversation row: tutor mark + bubble, or a right-aligned student bubble. */
export function MessageRow({ message }: MessageRowProps) {
  const isMaya = message.from === "maya";
  return (
    <div
      className={cn(
        "flex max-w-full animate-msg-in items-end gap-[10px]",
        isMaya && "flex-row-reverse",
      )}
    >
      {!isMaya && <TutorMark />}
      <div className={bubbleClass(isMaya)}>
        <div className="whitespace-pre-wrap leading-[1.5]">{message.text}</div>
      </div>
    </div>
  );
}
