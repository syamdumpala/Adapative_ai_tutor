import { Avatar, Badge, EmptyState, SearchInput } from "@/components";
import { cn } from "@/lib/cn";
import { healthChipTone, improvementColorClass } from "@/lib/tones";
import type { TeacherStudent } from "../data/teacher";

interface StudentPanelProps {
  students: TeacherStudent[];
  query: string;
  onQuery: (value: string) => void;
  onOpenStudent: (id: string) => void;
}

function StudentRow({
  student,
  onClick,
}: {
  student: TeacherStudent;
  onClick: () => void;
}) {
  const topics = Object.keys(student.eng).length;
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center gap-[13px] rounded-lg border border-line bg-card px-4 py-[14px] text-left shadow-soft transition hover:-translate-y-[2px] hover:border-ink3 hover:shadow-float"
    >
      <Avatar initials={student.initials} gradient={student.tone} size={42} />
      <div className="min-w-0 flex-1">
        <div className="text-[15px] font-bold">{student.name}</div>
        <div className="mt-[2px] text-[12px] text-ink2">
          {topics} topic{topics === 1 ? "" : "s"} explored
        </div>
      </div>
      <div className="flex-none text-right">
        <Badge tone="plain" className={healthChipTone[student.tone]}>
          {student.status}
        </Badge>
        <div
          className={cn(
            "mt-[5px] font-mono text-[11px] font-bold",
            improvementColorClass(student.improvement),
          )}
        >
          {student.improvement}
        </div>
      </div>
      <span className="flex-none text-[16px] text-ink3">›</span>
    </button>
  );
}

/** "Students" panel with search and per-student health chips. */
export function StudentPanel({
  students,
  query,
  onQuery,
  onOpenStudent,
}: StudentPanelProps) {
  const q = query.trim().toLowerCase();
  const filtered = q
    ? students.filter((student) => student.name.toLowerCase().includes(q))
    : students;
  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-baseline justify-between">
        <div className="font-display text-[16px] font-bold">Students</div>
        <span className="font-mono text-[11px] text-ink3">
          {students.length} students
        </span>
      </div>
      <SearchInput
        value={query}
        onChange={onQuery}
        placeholder="Search students…"
      />
      {filtered.map((student) => (
        <StudentRow
          key={student.id}
          student={student}
          onClick={() => onOpenStudent(student.id)}
        />
      ))}
      {filtered.length === 0 && (
        <EmptyState>No students match your search.</EmptyState>
      )}
    </section>
  );
}
