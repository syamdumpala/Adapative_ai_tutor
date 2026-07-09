import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TopicAnalyticsDTO } from "../../../api/student";
import { AXIS_TICK, CHART, masteryColor, TOOLTIP_STYLE } from "../chartTheme";
import { clip, toPct } from "../format";

interface RankDatum {
  name: string;
  mastery: number;
  color: string;
}

function toRanking(topics: TopicAnalyticsDTO[]): RankDatum[] {
  return topics
    .map((t) => ({
      name: clip(t.concept_name, 18),
      mastery: toPct(t.mastery),
      color: masteryColor(t.mastery),
    }))
    .sort((a, b) => b.mastery - a.mastery);
}

/** Horizontal ranking of topics by mastery; bar colour flags weak (coral) → strong (green). */
export function TopicRankingChart({ topics }: { topics: TopicAnalyticsDTO[] }) {
  const data = toRanking(topics);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        layout="vertical"
        data={data}
        margin={{ top: 4, right: 16, bottom: 0, left: 6 }}
      >
        <XAxis
          type="number"
          domain={[0, 100]}
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v: number) => `${v}%`}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={112}
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          cursor={{ fill: CHART.paper2 }}
          formatter={(v) => [`${v}%`, "Mastery"]}
        />
        <Bar dataKey="mastery" radius={[0, 4, 4, 0]} barSize={16}>
          {data.map((d) => (
            <Cell key={d.name} fill={d.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
