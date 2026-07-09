"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useResponsive, type Breakpoint } from "@/hooks/useResponsive";
import { useToast, type ToastController } from "@/hooks/useToast";
import { buildStudents, type TeacherStudent } from "../data/teacher";
import { initialsOf } from "../data/student";
import type { ModalKind, Role } from "../types";
import { type MiraChat, useMiraChat } from "./useMiraChat";
import { type TeacherNav, useTeacherNav } from "./useTeacherNav";

export interface TutorShell {
  bp: Breakpoint;
  toast: ToastController;
  chat: MiraChat;
  teacherNav: TeacherNav;
  role: Role;
  modal: ModalKind;
  students: TeacherStudent[];
  initials: string;
  setRole: (role: Role) => void;
  onLogoClick: () => void;
  onSimulateDay: () => void;
  onRestart: () => void;
  openModal: (modal: ModalKind) => void;
  closeModal: () => void;
  onStudentLogout: () => void;
  onTeacherLogout: () => void;
  onToTeacher: () => void;
}

/** Owns app-shell state (role, modal, toast) and the cross-cutting handlers. */
export function useTutorShell(
  studentName: string,
  initialRole: Role,
): TutorShell {
  const bp = useResponsive();
  const toast = useToast();
  const chat = useMiraChat(studentName);
  const teacherNav = useTeacherNav();
  const router = useRouter();
  const [role, setRoleState] = useState<Role>(initialRole);
  const [modal, setModal] = useState<ModalKind>(null);
  const students = useMemo(() => buildStudents(studentName), [studentName]);

  const goTeacher = () => {
    chat.commit();
    setRoleState("teacher");
  };

  return {
    bp,
    toast,
    chat,
    teacherNav,
    role,
    modal,
    students,
    initials: initialsOf(studentName),
    setRole: (next) =>
      next === "teacher" ? goTeacher() : setRoleState("student"),
    onLogoClick: () => role === "student" && chat.goHome(),
    onSimulateDay: () =>
      toast.show("+1 day simulated — revision dates advanced"),
    onRestart: () => {
      chat.restart();
      setModal(null);
      setRoleState("student");
    },
    openModal: setModal,
    closeModal: () => setModal(null),
    onStudentLogout: () => {
      toast.show("Signed out — this is a demo, your progress is kept");
      chat.goHome();
    },
    onTeacherLogout: () => router.push("/login"),
    onToTeacher: goTeacher,
  };
}
