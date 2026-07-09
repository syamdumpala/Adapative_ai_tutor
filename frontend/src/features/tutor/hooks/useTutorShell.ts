"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useResponsive, type Breakpoint } from "@/hooks/useResponsive";
import { useToast, type ToastController } from "@/hooks/useToast";
import type { TeacherStudent } from "../data/teacher";
import { initialsOf } from "../data/student";
import { signOut } from "@/features/auth/api";
import type { ModalKind, Role, StudentView } from "../types";
import { type MiraChat, useMiraChat } from "./useMiraChat";
import { type TeacherNav, useTeacherNav } from "./useTeacherNav";
import { useTeacherStudents } from "./useTeacherStudents";

export interface TutorShell {
  bp: Breakpoint;
  toast: ToastController;
  chat: MiraChat;
  teacherNav: TeacherNav;
  role: Role;
  modal: ModalKind;
  studentView: StudentView;
  students: TeacherStudent[];
  initials: string;
  onLogoClick: () => void;
  openModal: (modal: ModalKind) => void;
  closeModal: () => void;
  openAnalytics: () => void;
  backToHome: () => void;
  onLogout: () => void;
}

/** Owns app-shell state (modal, toast) and the cross-cutting handlers. The role
 * is fixed by the signed-in account — there is no in-app role switch. */
export function useTutorShell(
  studentName: string,
  initialRole: Role,
): TutorShell {
  const bp = useResponsive();
  const toast = useToast();
  const chat = useMiraChat();
  const teacherNav = useTeacherNav();
  const router = useRouter();
  const role = initialRole;
  const [modal, setModal] = useState<ModalKind>(null);
  const [studentView, setStudentView] = useState<StudentView>("home");
  const { students } = useTeacherStudents(role === "teacher");

  const goStudentHome = () => {
    setStudentView("home");
    chat.goHome();
  };

  return {
    bp,
    toast,
    chat,
    teacherNav,
    role,
    modal,
    studentView,
    students,
    initials: initialsOf(studentName),
    onLogoClick: () =>
      role === "student" ? goStudentHome() : teacherNav.goHome(),
    openModal: setModal,
    closeModal: () => setModal(null),
    openAnalytics: () => setStudentView("analytics"),
    backToHome: () => setStudentView("home"),
    onLogout: () => void signOut().finally(() => router.push("/login")),
  };
}
