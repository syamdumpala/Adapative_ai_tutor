"use client";

import { Toast } from "@/components";
import { MIRA_BACKDROP } from "@/lib/backdrop";
import { DEFAULT_STUDENT_NAME } from "./data/student";
import { type TutorShell, useTutorShell } from "./hooks/useTutorShell";
import { StudentArea } from "./student/StudentArea";
import { StudentModal } from "./student/StudentModal";
import { TeacherDashboard } from "./teacher/TeacherDashboard";
import { Topbar } from "./Topbar";
import type { Role } from "./types";

interface TutorAppProps {
  studentName?: string;
  initialRole?: Role;
  /** Celebrate correct answers with the burst animation. */
  celebrate?: boolean;
}

function AppBody({
  shell,
  studentName,
  celebrate,
}: {
  shell: TutorShell;
  studentName: string;
  celebrate: boolean;
}) {
  if (shell.role !== "student") {
    return (
      <TeacherDashboard
        nav={shell.teacherNav}
        students={shell.students}
        bp={shell.bp}
        onLogout={shell.onTeacherLogout}
      />
    );
  }
  return (
    <StudentArea
      chat={shell.chat}
      name={studentName}
      initials={shell.initials}
      bp={shell.bp}
      celebrate={celebrate}
      onProfile={() => shell.openModal("profile")}
      onPerformance={() => shell.openModal("performance")}
      onLogout={shell.onStudentLogout}
      onToTeacher={shell.onToTeacher}
    />
  );
}

/** Root of the Mira Tutor experience: topbar plus the student / teacher areas. */
export function TutorApp({
  studentName = DEFAULT_STUDENT_NAME,
  initialRole = "student",
  celebrate = true,
}: TutorAppProps) {
  const shell = useTutorShell(studentName, initialRole);
  const isStudent = shell.role === "student";

  return (
    <div
      className="flex h-screen flex-col overflow-hidden"
      style={{ background: MIRA_BACKDROP }}
    >
      <Topbar
        role={shell.role}
        onRole={shell.setRole}
        onLogoClick={shell.onLogoClick}
        isTeacher={!isStudent}
        onSimulateDay={shell.onSimulateDay}
        onRestart={shell.onRestart}
        showLabels={shell.bp !== "mobile"}
      />
      <Toast message={shell.toast.message} />
      {isStudent && (
        <StudentModal
          modal={shell.modal}
          onClose={shell.closeModal}
          name={studentName}
          initials={shell.initials}
        />
      )}
      <AppBody shell={shell} studentName={studentName} celebrate={celebrate} />
    </div>
  );
}
