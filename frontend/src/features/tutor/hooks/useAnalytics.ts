"use client";

import { useEffect, useState } from "react";
import {
  type AnalyticsDTO,
  fetchAnalytics,
  fetchTopicAnalytics,
  type TopicAnalyticsDTO,
} from "../api/student";

/** Async resource state shared by the analytics hooks. */
export interface Resource<T> {
  data: T | null;
  loading: boolean;
  error: boolean;
}

/** Run `load` once on mount, tracking loading/error and ignoring stale results. */
function useResource<T>(load: () => Promise<T>): Resource<T> {
  const [state, setState] = useState<Resource<T>>({
    data: null,
    loading: true,
    error: false,
  });
  useEffect(() => {
    let active = true;
    // Initial state is already `loading`; only the async settle updates state.
    load()
      .then(
        (data) => active && setState({ data, loading: false, error: false }),
      )
      .catch(
        () => active && setState({ data: null, loading: false, error: true }),
      );
    return () => {
      active = false;
    };
    // `load` is a stable module-level fetcher; run exactly once on mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return state;
}

/** Overall (subject-grain) learning analytics for the signed-in student. */
export function useAnalytics(): Resource<AnalyticsDTO> {
  return useResource(fetchAnalytics);
}

/** Per-topic (concept-grain) analytics for the signed-in student. */
export function useTopicAnalytics(): Resource<TopicAnalyticsDTO[]> {
  return useResource(async () => (await fetchTopicAnalytics()).topics);
}
