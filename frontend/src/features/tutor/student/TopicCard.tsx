import { Badge, GlyphTile } from "@/components";
import { cn } from "@/lib/cn";
import { truncateWords } from "@/lib/text";
import { ctaTextTone } from "@/lib/tones";
import type { Topic } from "../types";

interface TopicCardProps {
  topic: Topic;
  onClick: () => void;
}

/** A tappable topic tile with glyph, blurb, CTA and optional progress. */
export function TopicCard({ topic, onClick }: TopicCardProps) {
  const started = topic.progress > 0;
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex min-h-[172px] flex-col rounded-lg border border-line bg-card p-[18px] text-left shadow-soft transition hover:-translate-y-1 hover:border-line2 hover:shadow-float"
    >
      <div className="mb-[15px] flex items-start justify-between gap-[10px]">
        <GlyphTile glyph={topic.glyph} tone={topic.tone} size={46} />
        {topic.isNew && (
          <Badge tone="violet" mono className="text-[9px]">
            New
          </Badge>
        )}
      </div>
      <div className="font-display text-[19px] font-bold">{topic.name}</div>
      <div className="mt-[5px] flex-1 text-[13px] text-ink2" title={topic.desc}>
        {truncateWords(topic.desc, 5)}
      </div>
      <div className="mt-4 flex items-center justify-between gap-[10px]">
        <span className="font-mono text-[10.5px] text-ink3">{topic.meta}</span>
        <span
          className={cn("text-[12.5px] font-bold", ctaTextTone[topic.tone])}
        >
          {started ? "Continue" : "Start"} →
        </span>
      </div>
    </button>
  );
}
