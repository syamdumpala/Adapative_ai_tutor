import {
  Avatar,
  Badge,
  EmptyState,
  GlyphTile,
  SearchInput,
  StatCard,
} from "@/components";
import { understandingChipTone, understandingLabel } from "@/lib/tones";
import {
  type Engagement,
  type TeacherStudent,
  type TeacherTopic,
  topicAggregate,
} from "../data/teacher";

interface TopicDetailProps {
  topic: TeacherTopic;
  students: TeacherStudent[];
  query: string;
  onQuery: (value: string) => void;
  onOpenStudent: (id: string) => void;
}

function TopicHeader({ topic }: { topic: TeacherTopic }) {
  return (
    <div className="flex items-start gap-4">
      <GlyphTile glyph={topic.glyph} toneClassName={topic.tile} size={58} />
      <div className="min-w-0 flex-1">
        <div className="mb-[6px] font-mono text-[10px] uppercase tracking-[0.14em] text-ink3">
          Topic
        </div>
        <h1 className="text-[clamp(23px,3vw,31px)] font-extrabold">
          {topic.name}
        </h1>
        <p className="mt-[9px] max-w-[66ch] text-[14px] leading-[1.55] text-ink2">
          {topic.long}
        </p>
      </div>
    </div>
  );
}

function StudentRow({
  student,
  engagement,
  onClick,
}: {
  student: TeacherStudent;
  engagement: Engagement;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center gap-[13px] rounded-[14px] border border-line bg-card px-4 py-[13px] text-left shadow-soft transition hover:border-ink3"
    >
      <Avatar initials={student.initials} gradient={student.tone} size={40} />
      <div className="min-w-0 flex-1">
        <div className="text-[14px] font-bold">{student.name}</div>
        <div className="text-[11.5px] text-ink2">
          {engagement.asked} question{engagement.asked === 1 ? "" : "s"} asked
        </div>
      </div>
      <Badge tone="plain" className={understandingChipTone[engagement.u]}>
        {understandingLabel[engagement.u]}
      </Badge>
      <span className="flex-none text-[14px] text-ink3">›</span>
    </button>
  );
}

function OutcomeGrid({
  rows,
  topicId,
  onOpenStudent,
}: {
  rows: TeacherStudent[];
  topicId: string;
  onOpenStudent: (id: string) => void;
}) {
  return (
    <div className="grid gap-[10px] [grid-template-columns:repeat(auto-fill,minmax(250px,1fr))]">
      {rows.map((student) => (
        <StudentRow
          key={student.id}
          student={student}
          engagement={student.eng[topicId]!}
          onClick={() => onOpenStudent(student.id)}
        />
      ))}
    </div>
  );
}

function StudentOutcomes({
  topic,
  students,
  query,
  onQuery,
  onOpenStudent,
}: TopicDetailProps) {
  const engaged = students.filter((student) => student.eng[topic.id]);
  const q = query.trim().toLowerCase();
  const rows = q
    ? engaged.filter((student) => student.name.toLowerCase().includes(q))
    : engaged;
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="font-display text-[15px] font-bold">
          How each student did
        </div>
        {engaged.length > 0 && (
          <SearchInput
            value={query}
            onChange={onQuery}
            placeholder="Search students…"
            height={38}
            className="w-[min(260px,100%)]"
          />
        )}
      </div>
      {rows.length > 0 && (
        <OutcomeGrid
          rows={rows}
          topicId={topic.id}
          onOpenStudent={onOpenStudent}
        />
      )}
      {engaged.length > 0 && rows.length === 0 && (
        <EmptyState>No students match your search.</EmptyState>
      )}
      {engaged.length === 0 && (
        <EmptyState size="lg">
          No one has asked Mira about this topic yet.
        </EmptyState>
      )}
    </div>
  );
}

/** Topic drill-down: description, class stats, and per-student outcomes. */
export function TopicDetail(props: TopicDetailProps) {
  const agg = topicAggregate(props.students, props.topic.id);
  return (
    <div className="flex animate-fade-up flex-col gap-5">
      <TopicHeader topic={props.topic} />
      <div className="grid grid-cols-3 gap-3">
        <StatCard value={agg.students} label="Students asked" />
        <StatCard value={agg.questions} label="Questions to Mira" />
        <StatCard
          value={agg.students > 0 ? `${agg.understood}/${agg.students}` : "0"}
          label="Understood it"
          accent
        />
      </div>
      <StudentOutcomes {...props} />
    </div>
  );
}
