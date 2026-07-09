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
  goHome: () => void;
  openTopic: (id: string) => void;
  openStudent: (id: string) => void;
}

/** Teacher drill-down navigation + per-screen search state. */
export function useTeacherNav(): TeacherNav {
  const [screen, setScreen] = useState<TeacherScreen>("home");
  const [topicId, setTopicId] = useState("partition");
  const [studentId, setStudentId] = useState("maya");
  const [qTopics, setQTopics] = useState("");
  const [qStudents, setQStudents] = useState("");
  const [qTopicStu, setQTopicStu] = useState("");
  const [qStuTopics, setQStuTopics] = useState("");

  return {
    screen,
    topicId,
    studentId,
    qTopics,
    qStudents,
    qTopicStu,
    qStuTopics,
    setQTopics,
    setQStudents,
    setQTopicStu,
    setQStuTopics,
    goHome: () => setScreen("home"),
    openTopic: (id) => {
      setTopicId(id);
      setQTopicStu("");
      setScreen("topic");
    },
    openStudent: (id) => {
      setStudentId(id);
      setQStuTopics("");
      setScreen("student");
    },
  };
}
