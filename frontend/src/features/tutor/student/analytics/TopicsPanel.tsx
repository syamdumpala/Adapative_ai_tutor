import { Card } from "@/components";
import type { TopicAnalyticsDTO } from "../../api/student";
import { useTopicAnalytics } from "../../hooks/useAnalytics";
import { ChartCard } from "./ChartCard";
import { EffortScatter } from "./charts/EffortScatter";
import { MasteryConfidenceChart } from "./charts/MasteryConfidenceChart";
import { TopicRankingChart } from "./charts/TopicRankingChart";
import { UnderstandingDonut } from "./charts/UnderstandingDonut";
import { CHART_INFO } from "./chartInfo";
import { InfoDot } from "./InfoDot";
import { ReviewDueList } from "./ReviewDueList";

const EMPTY_TOPICS =
  "No topics yet — open a topic and ask a question to get started.";

function ReviewCard({ topics }: { topics: TopicAnalyticsDTO[] }) {
  return (
    <Card className="flex animate-fade-up flex-col rounded-md p-[clamp(14px,1.8vw,20px)]">
      <div className="mb-3 flex items-start justify-between gap-2">
        <div>
          <h3 className="text-[14px] font-bold text-ink">Review due</h3>
          <p className="mt-[2px] text-[12px] text-ink2">
            Topics to revisit next
          </p>
        </div>
        <InfoDot text={CHART_INFO.reviewDue} />
      </div>
      <ReviewDueList topics={topics} />
    </Card>
  );
}

function SecondaryCharts({
  topics,
  empty,
}: {
  topics: TopicAnalyticsDTO[];
  empty: boolean;
}) {
  const box = { isEmpty: empty, emptyMessage: EMPTY_TOPICS, height: 260 };
  return (
    <div className="grid gap-[clamp(12px,1.6vw,18px)] lg:grid-cols-2">
      <ChartCard
        title="Mastery vs confidence per topic"
        subtitle="Taller confidence bar = over-confident"
        info={CHART_INFO.masteryConfidence}
        {...box}
      >
        <MasteryConfidenceChart topics={topics} />
      </ChartCard>
      <ChartCard
        title="Effort vs mastery"
        subtitle="Bubble size = current streak"
        info={CHART_INFO.effort}
        {...box}
      >
        <EffortScatter topics={topics} />
      </ChartCard>
      <ChartCard
        title="Understanding mix"
        subtitle="Topics you've got, are getting, or are stuck on"
        info={CHART_INFO.understanding}
        isEmpty={empty}
        emptyMessage={EMPTY_TOPICS}
      >
        <UnderstandingDonut topics={topics} />
      </ChartCard>
      <ReviewCard topics={topics} />
    </div>
  );
}

/** Per-topic performance: ranking, calibration, understanding mix, effort, review queue. */
export function TopicsPanel() {
  const { data, loading } = useTopicAnalytics();
  const topics = data ?? [];
  const empty = !loading && topics.length === 0;

  return (
    <div className="flex flex-col gap-[clamp(12px,1.6vw,18px)]">
      <ChartCard
        title="Topic mastery ranking"
        subtitle="Strongest to weakest · colour flags where to focus"
        info={CHART_INFO.topicRanking}
        height={Math.max(200, topics.length * 34 + 60)}
        isEmpty={empty}
        emptyMessage={EMPTY_TOPICS}
      >
        <TopicRankingChart topics={topics} />
      </ChartCard>
      <SecondaryCharts topics={topics} empty={empty} />
    </div>
  );
}
