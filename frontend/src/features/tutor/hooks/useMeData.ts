"use client";

import { useEffect, useState } from "react";
import {
  fetchPerformance,
  fetchProfile,
  type PerformanceDTO,
  type ProfileDTO,
} from "../api/student";

/** Fetch the signed-in student's profile when the profile modal opens. */
export function useProfile(open: boolean): ProfileDTO | null {
  const [profile, setProfile] = useState<ProfileDTO | null>(null);
  useEffect(() => {
    if (!open) return;
    let active = true;
    fetchProfile()
      .then((data) => active && setProfile(data))
      .catch(() => active && setProfile(null));
    return () => {
      active = false;
    };
  }, [open]);
  return profile;
}

/** Fetch the student performance record when the performance modal opens. */
export function usePerformance(open: boolean): PerformanceDTO | null {
  const [perf, setPerf] = useState<PerformanceDTO | null>(null);
  useEffect(() => {
    if (!open) return;
    let active = true;
    fetchPerformance()
      .then((data) => active && setPerf(data))
      .catch(() => active && setPerf(null));
    return () => {
      active = false;
    };
  }, [open]);
  return perf;
}
