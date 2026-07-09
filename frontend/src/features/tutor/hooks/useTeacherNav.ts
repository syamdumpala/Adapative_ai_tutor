"use client";

import { useState } from "react";
import type { TeacherScreen } from "../types";

export interface TeacherNav {
  screen: TeacherScreen;
  topicId: string;
  studentId: string;
  qTopics: string;
  qStudents: string;
  qTopicStu: string;
  qStuTopics: string;
  setQTopics: (value: string) => void;
  setQStudents: (value: string) => void;
  setQTopicStu: (value: string) => void;
  setQStuTopics: (value: string) => void;
  /** True when there is a previous screen to return to. */
  canGoBack: boolean;
  goHome: () => void;
  goBack: () => void;
  openCatalog: () => void;
  openTopic: (id: string) => void;
  openStudent: (id: string) => void;
}

/** A snapshot of the full nav context, pushed on each drill-down. */
interface NavFrame {
  screen: TeacherScreen;
  topicId: string;
  studentId: string;
}

interface Queries {
  qTopics: string;
  qStudents: string;
  qTopicStu: string;
  qStuTopics: string;
  setQTopics: (value: string) => void;
  setQStudents: (value: string) => void;
  setQTopicStu: (value: string) => void;
  setQStuTopics: (value: string) => void;
}

/** Per-screen search-box state for the teacher dashboard. */
function useSearchQueries(): Queries {
  const [qTopics, setQTopics] = useState("");
  const [qStudents, setQStudents] = useState("");
  const [qTopicStu, setQTopicStu] = useState("");
  const [qStuTopics, setQStuTopics] = useState("");
  return {
    qTopics,
    qStudents,
    qTopicStu,
    qStuTopics,
    setQTopics,
    setQStudents,
    setQTopicStu,
    setQStuTopics,
  };
}

/** Teacher drill-down navigation with a back stack + per-screen search state. */
export function useTeacherNav(): TeacherNav {
  const [screen, setScreen] = useState<TeacherScreen>("home");
  const [topicId, setTopicId] = useState("partition");
  const [studentId, setStudentId] = useState("maya");
  const [history, setHistory] = useState<NavFrame[]>([]);
  const queries = useSearchQueries();
  const push = () =>
    setHistory((prev) => [...prev, { screen, topicId, studentId }]);
  return {
    screen,
    topicId,
    studentId,
    ...queries,
    canGoBack: history.length > 0,
    goHome: () => {
      setScreen("home");
      setHistory([]);
    },
    goBack: () => {
      const frame = history[history.length - 1];
      setHistory((prev) => prev.slice(0, -1));
      setScreen(frame?.screen ?? "home");
      setTopicId(frame?.topicId ?? topicId);
      setStudentId(frame?.studentId ?? studentId);
    },
    openCatalog: () => {
      push();
      setScreen("catalog");
    },
    openTopic: (id) => {
      push();
      setTopicId(id);
      queries.setQTopicStu("");
      setScreen("topic");
    },
    openStudent: (id) => {
      push();
      setStudentId(id);
      queries.setQStuTopics("");
      setScreen("student");
    },
  };
}
