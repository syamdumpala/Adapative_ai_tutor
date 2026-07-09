import { EmptyState, GlyphTile, SearchInput } from "@/components";
import { cn } from "@/lib/cn";
import {
  TEACHER_TOPICS,
  type TeacherStudent,
  type TeacherTopic,
  type TopicAggregate,
  topicAggregate,
} from "../data/teacher";

interface TopicPanelProps {
  students: TeacherStudent[];
  query: string;
  onQuery: (value: string) => void;
  onOpenTopic: (id: string) => void;
}

function topicStat(agg: TopicAggregate): { text: string; className: string } {
  if (agg.students === 0)
    return {
      text: "No questions yet",
      className: "font-mono text-[11px] text-ink3",
    };
  const color =
    agg.understood === agg.students
      ? "text-green-d"
      : agg.understood === 0
        ? "text-coral-d"
        : "text-amber";
  return {
    text: `${agg.understood}/${agg.students} got it`,
    className: cn("font-mono text-[12px] font-bold", color),
  };
}

function TopicRow({
  topic,
  agg,
  onClick,
}: {
  topic: TeacherTopic;
  agg: TopicAggregate;
  onClick: () => void;
}) {
  const stat = topicStat(agg);
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center gap-[14px] rounded-lg border border-line bg-card px-4 py-[14px] text-left shadow-soft transition hover:-translate-y-[2px] hover:border-ink3 hover:shadow-float"
    >
      <GlyphTile glyph={topic.glyph} toneClassName={topic.tile} size={46} />
      <div className="min-w-0 flex-1">
        <div className="text-[15px] font-bold">{topic.name}</div>
        <div className="mt-[2px] truncate text-[12px] text-ink2">
          {topic.short}
        </div>
      </div>
      <div className="flex-none text-right">
        <div className={stat.className}>{stat.text}</div>
        <div className="mt-1 text-[10.5px] text-ink3">
          {agg.students > 0 ? `${agg.questions} questions` : "—"}
        </div>
      </div>
      <span className="flex-none text-[16px] text-ink3">›</span>
    </button>
  );
}

/** "Topics & chapters" panel with search and class-wide understanding stats. */
export function TopicPanel({
  students,
  query,
  onQuery,
  onOpenTopic,
}: TopicPanelProps) {
  const q = query.trim().toLowerCase();
  const filtered = q
    ? TEACHER_TOPICS.filter((t) =>
        `${t.name} ${t.short}`.toLowerCase().includes(q),
      )
    : TEACHER_TOPICS;
  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-baseline justify-between">
        <div className="font-display text-[16px] font-bold">
          Topics &amp; chapters
        </div>
        <span className="font-mono text-[11px] text-ink3">
          {TEACHER_TOPICS.length} topics
        </span>
      </div>
      <SearchInput
        value={query}
        onChange={onQuery}
        placeholder="Search topics…"
      />
      {filtered.map((topic) => (
        <TopicRow
          key={topic.id}
          topic={topic}
          agg={topicAggregate(students, topic.id)}
          onClick={() => onOpenTopic(topic.id)}
        />
      ))}
      {filtered.length === 0 && (
        <EmptyState>No topics match your search.</EmptyState>
      )}
    </section>
  );
}
