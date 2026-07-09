"use client";

import { Toast } from "@/components";
import { MIRA_BACKDROP } from "@/lib/backdrop";
import { AccountModal } from "./AccountModal";
import { DEFAULT_STUDENT_NAME } from "./data/student";
import { type TutorShell, useTutorShell } from "./hooks/useTutorShell";
import { StudentArea } from "./student/StudentArea";
import { TeacherDashboard } from "./teacher/TeacherDashboard";
import { Topbar } from "./Topbar";
import type { Role } from "./types";

interface TutorAppProps {
  studentName?: string;
  initialRole?: Role;
}

function AppBody({
  shell,
  studentName,
}: {
  shell: TutorShell;
  studentName: string;
}) {
  if (shell.role !== "student") {
    return (
      <TeacherDashboard
        nav={shell.teacherNav}
        students={shell.students}
        bp={shell.bp}
        onLogout={shell.onLogout}
        onProfile={() => shell.openModal("profile")}
        name={studentName}
        initials={shell.initials}
      />
    );
  }
  return (
    <StudentArea
      chat={shell.chat}
      name={studentName}
      initials={shell.initials}
      bp={shell.bp}
      studentView={shell.studentView}
      onProfile={() => shell.openModal("profile")}
      onPerformance={() => shell.openModal("performance")}
      onAnalytics={shell.openAnalytics}
      onBackHome={shell.backToHome}
      onLogout={shell.onLogout}
    />
  );
}

/** Root of the Mira Tutor experience: topbar plus the student / teacher areas. */
export function TutorApp({
  studentName = DEFAULT_STUDENT_NAME,
  initialRole = "student",
}: TutorAppProps) {
  const shell = useTutorShell(studentName, initialRole);

  return (
    <div
      className="flex h-screen flex-col overflow-hidden"
      style={{ background: MIRA_BACKDROP }}
    >
      <Topbar onLogoClick={shell.onLogoClick} />
      <Toast message={shell.toast.message} />
      <AccountModal
        modal={shell.modal}
        onClose={shell.closeModal}
        name={studentName}
        initials={shell.initials}
      />
      <AppBody shell={shell} studentName={studentName} />
    </div>
  );
}
