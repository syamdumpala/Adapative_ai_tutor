import type { TopicAnalyticsDTO } from "../../../api/student";
import { clip, toPct } from "../format";
import { GroupedBars, type GroupedDatum } from "./GroupedBars";

function toData(topics: TopicAnalyticsDTO[]): GroupedDatum[] {
  return topics.map((t) => ({
    name: clip(t.concept_name, 12),
    mastery: toPct(t.mastery),
    confidence: toPct(t.confidence),
  }));
}

/** Per-topic mastery vs confidence; a taller confidence bar flags over-confidence. */
export function MasteryConfidenceChart({
  topics,
}: {
  topics: TopicAnalyticsDTO[];
}) {
  return <GroupedBars data={toData(topics)} angled />;
}
