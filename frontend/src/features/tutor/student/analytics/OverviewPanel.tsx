import { StatCard } from "@/components";
import type { PerformanceDTO } from "../../api/student";
import { useAnalytics } from "../../hooks/useAnalytics";
import { usePerformance } from "../../hooks/useMeData";
import { ChartCard } from "./ChartCard";
import { MasteryTrendChart } from "./charts/MasteryTrendChart";
import { MisconceptionDonut } from "./charts/MisconceptionDonut";
import { SubjectBars } from "./charts/SubjectBars";

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

/** Overall performance: KPI tiles + mastery/confidence trend, misconceptions, subjects. */
export function OverviewPanel() {
  const perf = usePerformance(true);
  const { data, loading } = useAnalytics();
  const points = data?.points ?? [];
  const subjects = data?.by_subject ?? [];
  const noPoints = !loading && points.length === 0;

  return (
    <div className="flex flex-col gap-[clamp(12px,1.6vw,18px)]">
      <KpiRow perf={perf} />
      <ChartCard
        title="Mastery & confidence over time"
        subtitle="Every completed session · coral dots flag a misconception"
        height={280}
        isEmpty={noPoints}
      >
        <MasteryTrendChart points={points} />
      </ChartCard>
      <div className="grid gap-[clamp(12px,1.6vw,18px)] lg:grid-cols-2">
        <ChartCard
          title="Misconceptions by type"
          subtitle="How often each pattern showed up"
          isEmpty={!loading && points.every((p) => !p.misconception_category)}
          emptyMessage="No misconceptions flagged — nice."
        >
          <MisconceptionDonut points={points} />
        </ChartCard>
        <ChartCard
          title="Mastery vs confidence by subject"
          subtitle="Mean across each subject's sessions"
          isEmpty={!loading && subjects.length === 0}
        >
          <SubjectBars rows={subjects} />
        </ChartCard>
      </div>
    </div>
  );
}
