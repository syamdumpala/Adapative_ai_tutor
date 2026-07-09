import { Badge, GlyphTile, ProgressBar } from "@/components";
import { cn } from "@/lib/cn";
import { ctaTextTone, progressFillTone } from "@/lib/tones";
import type { Subject } from "../types";

interface SubjectCardProps {
  subject: Subject;
  onClick: () => void;
}

/** A tappable subject tile with glyph, blurb, CTA and optional progress. */
export function SubjectCard({ subject, onClick }: SubjectCardProps) {
  const started = subject.progress > 0;
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex min-h-[172px] flex-col rounded-lg border border-line bg-card p-[18px] text-left shadow-soft transition hover:-translate-y-1 hover:border-line2 hover:shadow-float"
    >
      <div className="mb-[15px] flex items-start justify-between gap-[10px]">
        <GlyphTile glyph={subject.glyph} tone={subject.tone} size={46} />
        {subject.isNew && (
          <Badge tone="violet" mono className="text-[9px]">
            New
          </Badge>
        )}
      </div>
      <div className="font-display text-[19px] font-bold">{subject.name}</div>
      <div className="mt-[5px] flex-1 text-[13px] text-ink2">
        {subject.desc}
      </div>
      <div className="mt-4 flex items-center justify-between gap-[10px]">
        <span className="font-mono text-[10.5px] text-ink3">
          {subject.meta}
        </span>
        <span
          className={cn("text-[12.5px] font-bold", ctaTextTone[subject.tone])}
        >
          {started ? "Continue" : "Start"} →
        </span>
      </div>
      {started && (
        <ProgressBar
          value={subject.progress}
          fillClassName={progressFillTone[subject.tone]}
          className="mt-[13px]"
        />
      )}
    </button>
  );
}
