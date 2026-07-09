import { GlyphTile } from "@/components";
import { masteryFillClass } from "@/lib/tones";
import type { TopicAnalyticsDTO } from "../../api/student";
import { safeTone } from "./chartTheme";
import { pct, shortDate } from "./format";

/** Topics with a scheduled review, soonest first. */
function dueTopics(topics: TopicAnalyticsDTO[]): TopicAnalyticsDTO[] {
  return topics
    .filter((t) => t.next_review)
    .sort((a, b) => (a.next_review ?? "").localeCompare(b.next_review ?? ""));
}

function ReviewRow({ topic }: { topic: TopicAnalyticsDTO }) {
  return (
    <li className="flex items-center gap-3 rounded-sm bg-paper2 px-3 py-[10px]">
      <GlyphTile
        glyph={topic.glyph || "◍"}
        tone={safeTone(topic.tone)}
        size={34}
      />
      <div className="min-w-0 flex-1">
        <div className="truncate text-[13px] font-semibold text-ink">
          {topic.concept_name}
        </div>
        <div className="mt-[3px] h-[5px] w-full overflow-hidden rounded-full bg-line">
          <div
            className={`h-full rounded-full ${masteryFillClass(topic.mastery)}`}
            style={{ width: pct(topic.mastery) }}
          />
        </div>
      </div>
      <span className="flex-none text-[11.5px] font-semibold text-ink2">
        {shortDate(topic.next_review, "—")}
      </span>
    </li>
  );
}

/** "Review due" rail: which topics to revisit next, with current mastery. */
export function ReviewDueList({ topics }: { topics: TopicAnalyticsDTO[] }) {
  const due = dueTopics(topics);
  if (due.length === 0) {
    return (
      <p className="rounded-sm bg-paper2 px-3 py-4 text-center text-[12.5px] text-ink2">
        Nothing due for review — you&apos;re all caught up.
      </p>
    );
  }
  return (
    <ul className="flex flex-col gap-2">
      {due.map((t) => (
        <ReviewRow key={t.concept_id} topic={t} />
      ))}
    </ul>
  );
}
