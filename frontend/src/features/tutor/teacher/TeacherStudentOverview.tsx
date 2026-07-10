"use client";

import {
  useTeacherStudentAnalytics,
  useTeacherStudentPerformance,
} from "../hooks/useAnalytics";
import { OverviewCharts } from "../student/analytics/OverviewCharts";

/** A student's overall performance graphs (the same block they see on their own
 * "My progress" overview), shown read-only in the teacher's student profile. */
export function TeacherStudentOverview({ studentId }: { studentId: string }) {
  const analytics = useTeacherStudentAnalytics(studentId);
  const performance = useTeacherStudentPerformance(studentId);
  return (
    <OverviewCharts
      points={analytics.data?.points ?? []}
      subjects={analytics.data?.by_subject ?? []}
      perf={performance.data}
      loading={analytics.loading}
    />
  );
}
