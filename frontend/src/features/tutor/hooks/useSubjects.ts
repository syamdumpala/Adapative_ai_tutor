"use client";

import { useEffect, useState } from "react";
import { fetchSubjects } from "../api/student";
import { SUBJECTS } from "../data/subjects";
import type { Subject } from "../types";

/**
 * Live subject catalog from `GET /subjects` (with per-student progress).
 * Starts from the static catalog so first paint is instant, then swaps in the
 * backend list once it loads.
 */
export function useSubjects(): Subject[] {
  const [subjects, setSubjects] = useState<Subject[]>(SUBJECTS);

  useEffect(() => {
    let active = true;
    fetchSubjects()
      .then((live) => {
        if (active && live.length) setSubjects(live);
      })
      .catch(() => {
        /* keep the static fallback on error */
      });
    return () => {
      active = false;
    };
  }, []);

  return subjects;
}
