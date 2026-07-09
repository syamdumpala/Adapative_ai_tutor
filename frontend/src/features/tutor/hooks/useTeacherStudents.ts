"use client";

import { useEffect, useState } from "react";
import { fetchRoster } from "../api/teacher";
import type { TeacherStudent } from "../data/teacher";

interface RosterState {
  students: TeacherStudent[];
  loading: boolean;
  error: string | null;
}

/**
 * Load the teacher roster (with each student's per-topic engagement) from the
 * backend once the dashboard is active. Screens filter this set client-side;
 * the endpoints also support server-side `q`/sort/filter for larger classes.
 */
export function useTeacherStudents(enabled: boolean): RosterState {
  const [state, setState] = useState<RosterState>({
    students: [],
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    fetchRoster()
      .then((students) => {
        if (active) setState({ students, loading: false, error: null });
      })
      .catch((err: unknown) => {
        if (active) {
          const message =
            err instanceof Error ? err.message : "Failed to load students.";
          setState({ students: [], loading: false, error: message });
        }
      });
    return () => {
      active = false;
    };
  }, [enabled]);

  return state;
}
