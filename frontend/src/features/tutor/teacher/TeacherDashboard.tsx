import type { Breakpoint } from "@/hooks/useResponsive";
import { type TeacherStudent, studentById, topicById } from "../data/teacher";
import type { TeacherNav } from "../hooks/useTeacherNav";
import { StudentDetail } from "./StudentDetail";
import { TeacherHome } from "./TeacherHome";
import { TeacherToolbar } from "./TeacherToolbar";
import { TopicCatalog } from "./TopicCatalog";
import { TopicDetail } from "./TopicDetail";

interface TeacherDashboardProps {
  nav: TeacherNav;
  students: TeacherStudent[];
  bp: Breakpoint;
  onLogout: () => void;
  onProfile: () => void;
  name: string;
  initials: string;
}

function screenBody(
  nav: TeacherNav,
  students: TeacherStudent[],
  bp: Breakpoint,
  name: string,
) {
  if (nav.screen === "catalog") {
    return <TopicCatalog />;
  }
  if (nav.screen === "topic") {
    return (
      <TopicDetail
        topic={topicById(nav.topicId)}
        students={students}
        query={nav.qTopicStu}
        onQuery={nav.setQTopicStu}
        onOpenStudent={nav.openStudent}
      />
    );
  }
  if (nav.screen === "student") {
    return (
      <StudentDetail
        student={studentById(students, nav.studentId)}
        query={nav.qStuTopics}
        onQuery={nav.setQStuTopics}
        onOpenTopic={nav.openTopic}
      />
    );
  }
  return <TeacherHome students={students} bp={bp} nav={nav} name={name} />;
}

/** Teacher dashboard shell: toolbar over home / topic / student screens. */
export function TeacherDashboard({
  nav,
  students,
  bp,
  onLogout,
  onProfile,
  name,
  initials,
}: TeacherDashboardProps) {
  return (
    <main
      className="scrolly flex-1 overflow-auto p-[clamp(16px,3vw,34px)]"
      data-screen="teacher"
    >
      <div className="mx-auto flex max-w-[1240px] flex-col gap-5">
        <TeacherToolbar
          screen={nav.screen}
          canGoBack={nav.canGoBack}
          onBack={nav.goBack}
          onCatalog={nav.openCatalog}
          onProfile={onProfile}
          onLogout={onLogout}
          name={name}
          initials={initials}
        />
        {screenBody(nav, students, bp, name)}
      </div>
    </main>
  );
}
