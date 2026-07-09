import { Badge, type BadgeTone, GlyphTile, IconButton } from "@/components";
import type { ChatStatus, Subject } from "../types";

interface ChatHeaderProps {
  subject: Subject;
  status: ChatStatus;
  title: string;
  onBack: () => void;
}

interface HeaderInfo {
  title: string;
  subtitle: string;
  pill: string;
  tone: BadgeTone;
}

function headerInfo(
  subject: Subject,
  status: ChatStatus,
  title: string,
): HeaderInfo {
  if (status === "draft") {
    return {
      title: subject.name,
      subtitle: "New chat",
      pill: "New",
      tone: "neutral",
    };
  }
  if (status === "completed") {
    return {
      title: title || subject.name,
      subtitle: `${subject.name} · completed`,
      pill: "Completed",
      tone: "green",
    };
  }
  return {
    title: title || subject.name,
    subtitle: `${subject.name} · in progress`,
    pill: "In progress",
    tone: "amber",
  };
}

/** Chat screen header: back, subject glyph, title/subtitle and status pill. */
export function ChatHeader({
  subject,
  status,
  title,
  onBack,
}: ChatHeaderProps) {
  const info = headerInfo(subject, status, title);
  return (
    <div className="flex items-center gap-[11px] border-b border-line bg-paper px-[clamp(12px,2vw,20px)] py-[11px]">
      <IconButton
        variant="card"
        onClick={onBack}
        title="Back to subjects"
        className="text-[18px]"
      >
        ‹
      </IconButton>
      <GlyphTile glyph={subject.glyph} tone={subject.tone} size={34} />
      <div className="min-w-0 flex-1">
        <div className="truncate text-[14.5px] font-bold">{info.title}</div>
        <div className="text-[11.5px] text-ink2">{info.subtitle}</div>
      </div>
      <Badge tone={info.tone}>{info.pill}</Badge>
    </div>
  );
}
