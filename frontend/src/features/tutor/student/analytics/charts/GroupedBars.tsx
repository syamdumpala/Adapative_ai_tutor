import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AXIS_TICK,
  CHART,
  CONFIDENCE_COLOR,
  MASTERY_COLOR,
  TOOLTIP_STYLE,
} from "../chartTheme";

export interface GroupedDatum {
  name: string;
  mastery: number;
  confidence: number;
}

const AXIS = { tick: AXIS_TICK, tickLine: false, axisLine: false } as const;
const YPCT = {
  domain: [0, 100] as [number, number],
  tickFormatter: (v: number) => `${v}%`,
};
const SERIES = [
  { key: "mastery", name: "Mastery", fill: MASTERY_COLOR },
  { key: "confidence", name: "Confidence", fill: CONFIDENCE_COLOR },
] as const;

/** Grouped mastery-vs-confidence bars, shared by the subject and per-topic charts. */
export function GroupedBars({
  data,
  angled = false,
}: {
  data: GroupedDatum[];
  angled?: boolean;
}) {
  const xExtra = angled
    ? { interval: 0, angle: -18, textAnchor: "end" as const, height: 48 }
    : {};
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={data}
        margin={{ top: 6, right: 10, bottom: 0, left: -18 }}
      >
        <CartesianGrid
          stroke={CHART.line}
          strokeDasharray="3 3"
          vertical={false}
        />
        <XAxis dataKey="name" {...AXIS} {...xExtra} />
        <YAxis {...AXIS} {...YPCT} />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          cursor={{ fill: CHART.paper2 }}
          formatter={(v) => `${v}%`}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {SERIES.map((s) => (
          <Bar
            key={s.key}
            dataKey={s.key}
            name={s.name}
            fill={s.fill}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
