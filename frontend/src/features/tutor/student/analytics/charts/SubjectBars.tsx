import type { SubjectAnalyticsDTO } from "../../../api/student";
import { clip, toPct } from "../format";
import { GroupedBars, type GroupedDatum } from "./GroupedBars";

function toData(rows: SubjectAnalyticsDTO[]): GroupedDatum[] {
  return rows.map((r, i) => ({
    name: clip(r.subject_name ?? r.subject_id ?? `Subject ${i + 1}`),
    mastery: toPct(r.mastery),
    confidence: toPct(r.confidence),
  }));
}

/** Grouped bars: mean mastery vs confidence per subject (across each subject's sessions). */
export function SubjectBars({ rows }: { rows: SubjectAnalyticsDTO[] }) {
  return <GroupedBars data={toData(rows)} />;
}
