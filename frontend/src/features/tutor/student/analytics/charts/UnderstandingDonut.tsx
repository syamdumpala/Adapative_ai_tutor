import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { understandingLabel, type Understanding } from "@/lib/tones";
import type { TopicAnalyticsDTO } from "../../../api/student";
import { TOOLTIP_STYLE, understandingColor } from "../chartTheme";

const ORDER: Understanding[] = ["yes", "partial", "no"];

interface Slice {
  key: Understanding;
  name: string;
  value: number;
}

function toSlices(topics: TopicAnalyticsDTO[]): Slice[] {
  const counts: Record<Understanding, number> = { yes: 0, partial: 0, no: 0 };
  for (const t of topics) {
    if (
      t.understanding === "yes" ||
      t.understanding === "partial" ||
      t.understanding === "no"
    )
      counts[t.understanding] += 1;
  }
  return ORDER.filter((k) => counts[k] > 0).map((k) => ({
    key: k,
    name: understandingLabel[k],
    value: counts[k],
  }));
}

/** How many topics the student has "got it" / "getting there" / is "stuck" on. */
export function UnderstandingDonut({
  topics,
}: {
  topics: TopicAnalyticsDTO[];
}) {
  const data = toSlices(topics);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius="55%"
          outerRadius="82%"
          paddingAngle={2}
          stroke="#fff"
          strokeWidth={2}
        >
          {data.map((slice) => (
            <Cell key={slice.key} fill={understandingColor[slice.key]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          formatter={(v) => [`${v} topics`, ""]}
        />
        <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
