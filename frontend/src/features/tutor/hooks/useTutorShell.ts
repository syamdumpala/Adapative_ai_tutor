"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useResponsive, type Breakpoint } from "@/hooks/useResponsive";
import { useToast, type ToastController } from "@/hooks/useToast";
import type { TeacherStudent } from "../data/teacher";
import { initialsOf } from "../data/student";
import { signOut } from "@/features/auth/api";
import type { ModalKind, Role } from "../types";
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
  students: TeacherStudent[];
  initials: string;
  onLogoClick: () => void;
  openModal: (modal: ModalKind) => void;
  closeModal: () => void;
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
  const { students } = useTeacherStudents(role === "teacher");

  return {
    bp,
    toast,
    chat,
    teacherNav,
    role,
    modal,
    students,
    initials: initialsOf(studentName),
    onLogoClick: () => role === "student" && chat.goHome(),
    openModal: setModal,
    closeModal: () => setModal(null),
    onLogout: () => void signOut().finally(() => router.push("/login")),
  };
}
