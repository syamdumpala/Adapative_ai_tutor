import { StatCard } from "@/components";
import type {
  AnalyticsPointDTO,
  PerformanceDTO,
  SubjectAnalyticsDTO,
} from "../../api/student";
import { ChartCard } from "./ChartCard";
import { MasteryTrendChart } from "./charts/MasteryTrendChart";
import { MisconceptionDonut } from "./charts/MisconceptionDonut";
import { SubjectBars } from "./charts/SubjectBars";
import { CHART_INFO } from "./chartInfo";

export interface OverviewChartsProps {
  points: AnalyticsPointDTO[];
  subjects: SubjectAnalyticsDTO[];
  perf: PerformanceDTO | null;
  loading: boolean;
}

function KpiRow({ perf }: { perf: PerformanceDTO | null }) {
  const stats = perf?.stats ?? [];
  if (stats.length === 0) return null;
  return (
    <div className="grid animate-fade-up grid-cols-2 gap-[10px] lg:grid-cols-4">
      {stats.map((stat) => (
        <StatCard
          key={stat.key}
          value={stat.value}
          label={stat.label}
          background="card"
          valueClassName={stat.value_class}
        />
      ))}
    </div>
  );
}

/** Presentational "overall performance" block (KPIs + trend, misconceptions,
 * subjects) — data comes in as props so it works for both the student's own
 * `/me/*` and a teacher viewing a specific student. */
export function OverviewCharts({
  points,
  subjects,
  perf,
  loading,
}: OverviewChartsProps) {
  const noPoints = !loading && points.length === 0;
  return (
    <div className="flex flex-col gap-[clamp(12px,1.6vw,18px)]">
      <KpiRow perf={perf} />
      <ChartCard
        title="Mastery, confidence & misconfidence over time"
        subtitle="Every completed session · left axis %, right axis Misconfidence"
        info={CHART_INFO.trend}
        height={300}
        isEmpty={noPoints}
      >
        <MasteryTrendChart points={points} />
      </ChartCard>
      <div className="grid gap-[clamp(12px,1.6vw,18px)] lg:grid-cols-2">
        <ChartCard
          title="Misconceptions by type"
          subtitle="How often each pattern showed up"
          info={CHART_INFO.misconceptionDonut}
          isEmpty={!loading && points.every((p) => !p.misconception_category)}
          emptyMessage="No misconceptions flagged — nice."
        >
          <MisconceptionDonut points={points} />
        </ChartCard>
        <ChartCard
          title="Mastery vs confidence by subject"
          subtitle="Mean across each subject's sessions"
          info={CHART_INFO.subjectBars}
          isEmpty={!loading && subjects.length === 0}
        >
          <SubjectBars rows={subjects} />
        </ChartCard>
      </div>
    </div>
  );
}
