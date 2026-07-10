import type { Breakpoint } from "@/hooks/useResponsive";
import { cn } from "@/lib/cn";
import type { TeacherStudent } from "../data/teacher";
import type { TeacherNav } from "../hooks/useTeacherNav";
import { StudentPanel } from "./StudentPanel";
import { TopicPanel } from "./TopicPanel";

interface TeacherHomeProps {
  students: TeacherStudent[];
  bp: Breakpoint;
  nav: TeacherNav;
  name: string;
}

/** Teacher landing: class heading over the topics and students panels. */
export function TeacherHome({ students, bp, nav, name }: TeacherHomeProps) {
  return (
    <>
      <div className="animate-fade-up">
        <h1 className="text-[clamp(26px,4vw,36px)] font-extrabold">
          Hello {name}
        </h1>
        <div className="mt-[5px] text-[13.5px] text-ink2">
          Open a topic to see how the class is doing, or a student to see their
          progress.
        </div>
      </div>
      <div
        className={cn(
          "grid items-start gap-5",
          bp === "mobile" ? "grid-cols-1" : "grid-cols-2",
        )}
      >
        <TopicPanel
          students={students}
          query={nav.qTopics}
          onQuery={nav.setQTopics}
          onOpenTopic={nav.openTopic}
        />
        <StudentPanel
          students={students}
          query={nav.qStudents}
          onQuery={nav.setQStudents}
          onOpenStudent={nav.openStudent}
        />
      </div>
    </>
  );
}
