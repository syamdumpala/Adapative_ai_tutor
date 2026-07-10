import {
  Avatar,
  Badge,
  EmptyState,
  ProgressBar,
  SearchInput,
  StatCard,
} from "@/components";
import {
  healthChipTone,
  masteryFillClass,
  understandingChipTone,
  understandingLabel,
} from "@/lib/tones";
import {
  type Engagement,
  type TeacherStudent,
  topicById,
} from "../data/teacher";
import { TeacherStudentOverview } from "./TeacherStudentOverview";

interface StudentDetailProps {
  student: TeacherStudent;
  query: string;
  onQuery: (value: string) => void;
  onOpenTopic: (id: string) => void;
}

function StudentDetailHeader({
  student,
  topicCount,
}: {
  student: TeacherStudent;
  topicCount: number;
}) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      <Avatar initials={student.initials} gradient={student.tone} size={58} />
      <div className="min-w-0 flex-1">
        <div className="mb-[6px] font-mono text-[10px] uppercase tracking-[0.14em] text-ink3">
          Student
        </div>
        <h1 className="text-[clamp(23px,3vw,31px)] font-extrabold">
          {student.name}
        </h1>
        <div className="mt-[6px] text-[13px] text-ink2">
          {topicCount} topics · {student.status.toLowerCase()}
        </div>
      </div>
      <Badge tone="plain" className={healthChipTone[student.tone]}>
        {student.status}
      </Badge>
    </div>
  );
}

function TopicProgressRow({
  name,
  engagement,
  delaySec,
}: {
  name: string;
  engagement: Engagement;
  delaySec: number;
}) {
  return (
    <div
      onClick={() => {}}
      className="flex items-center gap-[14px] rounded-[14px] border border-line bg-card px-4 py-[14px] text-left shadow-soft transition hover:border-ink3"
    >
      <div className="min-w-0 flex-1">
        <div className="mb-[9px] flex items-center gap-[9px]">
          <span className="text-[14px] font-bold">{name}</span>
          <Badge tone="plain" className={understandingChipTone[engagement.u]}>
            {understandingLabel[engagement.u]}
          </Badge>
        </div>
        <div className="flex items-center gap-[11px]">
          <ProgressBar
            value={engagement.m}
            fillClassName={masteryFillClass(engagement.m)}
            height={8}
            delaySec={delaySec}
            className="flex-1"
          />
          <span className="w-9 text-right font-mono text-[11px] text-ink3">
            {Math.round(engagement.m * 100)}%
          </span>
        </div>
      </div>
    </div>
  );
}

function ExploredTopics({ student, query, onQuery }: StudentDetailProps) {
  const firstName = student.name.split(" ")[0] ?? student.name;
  const q = query.trim().toLowerCase();
  const items = Object.keys(student.eng).map((id, index) => ({
    id,
    topic: topicById(id),
    engagement: student.eng[id]!,
    index,
  }));
  const rows = q
    ? items.filter((item) => item.topic.name.toLowerCase().includes(q))
    : items;
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="font-display text-[15px] font-bold">
          Topics {firstName} has explored
        </div>
        <SearchInput
          value={query}
          onChange={onQuery}
          placeholder="Search topics…"
          height={38}
          className="w-[min(260px,100%)]"
        />
      </div>
      {rows.length > 0 && (
        <div className="flex flex-col gap-[10px]">
          {rows.map((item) => (
            <TopicProgressRow
              key={item.id}
              name={item.topic.name}
              engagement={item.engagement}
              delaySec={item.index * 0.06}
            />
          ))}
        </div>
      )}
      {rows.length === 0 && (
        <EmptyState>No topics match your search.</EmptyState>
      )}
    </div>
  );
}

/** Student drill-down: header, progress stats, and explored-topic mastery. */
export function StudentDetail(props: StudentDetailProps) {
  const { student } = props;
  const topicIds = Object.keys(student.eng);
  const totalQuestions = topicIds.reduce(
    (sum, id) => sum + student.eng[id]!.asked,
    0,
  );
  return (
    <div className="flex animate-fade-up flex-col gap-5">
      <StudentDetailHeader student={student} topicCount={topicIds.length} />
      <div className="grid grid-cols-3 gap-3">
        <StatCard value={student.improvement} label="Improvement" accent />
        <StatCard value={topicIds.length} label="Topics explored" />
        <StatCard value={totalQuestions} label="Questions asked" />
      </div>
      <div>
        <div className="mb-3 font-display text-[15px] font-bold">
          Overall performance
        </div>
        <TeacherStudentOverview key={student.id} studentId={student.id} />
      </div>
      <ExploredTopics {...props} />
    </div>
  );
}
