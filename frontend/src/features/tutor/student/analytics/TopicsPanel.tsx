import { Card } from "@/components";
import type { TopicAnalyticsDTO } from "../../api/student";
import { useTopicAnalytics } from "../../hooks/useAnalytics";
import { ChartCard } from "./ChartCard";
import { EffortScatter } from "./charts/EffortScatter";
import { MasteryConfidenceChart } from "./charts/MasteryConfidenceChart";
import { TopicRankingChart } from "./charts/TopicRankingChart";
import { UnderstandingDonut } from "./charts/UnderstandingDonut";
import { ReviewDueList } from "./ReviewDueList";

const EMPTY_TOPICS =
  "No topics yet — open a topic and ask a question to get started.";

function ReviewCard({ topics }: { topics: TopicAnalyticsDTO[] }) {
  return (
    <Card className="flex animate-fade-up flex-col rounded-md p-[clamp(14px,1.8vw,20px)]">
      <h3 className="mb-1 text-[14px] font-bold text-ink">Review due</h3>
      <p className="mb-3 text-[12px] text-ink2">Topics to revisit next</p>
      <ReviewDueList topics={topics} />
    </Card>
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
        height={Math.max(200, topics.length * 34 + 60)}
        isEmpty={empty}
        emptyMessage={EMPTY_TOPICS}
      >
        <TopicRankingChart topics={topics} />
      </ChartCard>
      <div className="grid gap-[clamp(12px,1.6vw,18px)] lg:grid-cols-2">
        <ChartCard
          title="Mastery vs confidence per topic"
          subtitle="Taller confidence bar = over-confident"
          height={260}
          isEmpty={empty}
          emptyMessage={EMPTY_TOPICS}
        >
          <MasteryConfidenceChart topics={topics} />
        </ChartCard>
        <ChartCard
          title="Effort vs mastery"
          subtitle="Bubble size = current streak"
          height={260}
          isEmpty={empty}
          emptyMessage={EMPTY_TOPICS}
        >
          <EffortScatter topics={topics} />
        </ChartCard>
        <ChartCard
          title="Understanding mix"
          subtitle="Topics you've got, are getting, or are stuck on"
          isEmpty={empty}
          emptyMessage={EMPTY_TOPICS}
        >
          <UnderstandingDonut topics={topics} />
        </ChartCard>
        <ReviewCard topics={topics} />
      </div>
    </div>
  );
}
