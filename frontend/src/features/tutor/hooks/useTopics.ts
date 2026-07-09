"use client";

import { useEffect, useState } from "react";
import { fetchTopics } from "../api/catalog";
import { TOPICS } from "../data/topics";
import type { Topic } from "../types";

/**
 * Live topic catalog from `GET /subjects` (with per-student progress).
 * Starts from the static catalog so first paint is instant, then swaps in the
 * backend list once it loads.
 */
export function useTopics(): Topic[] {
  const [topics, setTopics] = useState<Topic[]>(TOPICS);

  useEffect(() => {
    let active = true;
    fetchTopics()
      .then((live) => {
        if (active && live.length) setTopics(live);
      })
      .catch(() => {
        /* keep the static fallback on error */
      });
    return () => {
      active = false;
    };
  }, []);

  return topics;
}
