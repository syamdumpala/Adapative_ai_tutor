import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { AnalyticsPointDTO } from "../../../api/student";
import { CATEGORY_COLORS, TOOLTIP_STYLE } from "../chartTheme";

interface Slice {
  name: string;
  value: number;
}

/** Tally misconception categories across the completed-session points. */
export function misconceptionSlices(points: AnalyticsPointDTO[]): Slice[] {
  const counts = new Map<string, number>();
  for (const p of points) {
    const key = p.misconception_category;
    if (key) counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return [...counts.entries()]
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

/** Donut of how often each misconception category showed up across sessions. */
export function MisconceptionDonut({
  points,
}: {
  points: AnalyticsPointDTO[];
}) {
  const data = misconceptionSlices(points);
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
          {data.map((slice, i) => (
            <Cell
              key={slice.name}
              fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip contentStyle={TOOLTIP_STYLE} />
        <Legend
          iconType="circle"
          wrapperStyle={{ fontSize: 12 }}
          formatter={(value: string) => value}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
