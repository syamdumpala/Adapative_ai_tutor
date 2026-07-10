import { useAnalytics } from "../../hooks/useAnalytics";
import { usePerformance } from "../../hooks/useMeData";
import { OverviewCharts } from "./OverviewCharts";

/** The signed-in student's own overall performance (from `/me/*`). */
export function OverviewPanel() {
  const perf = usePerformance(true);
  const { data, loading } = useAnalytics();
  return (
    <OverviewCharts
      points={data?.points ?? []}
      subjects={data?.by_subject ?? []}
      perf={perf}
      loading={loading}
    />
  );
}
