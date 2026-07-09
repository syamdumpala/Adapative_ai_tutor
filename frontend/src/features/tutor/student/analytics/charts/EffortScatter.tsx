import {
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import type { TopicAnalyticsDTO } from "../../../api/student";
import {
  AXIS_TICK,
  CHART,
  safeTone,
  TOOLTIP_STYLE,
  toneColor,
} from "../chartTheme";
import { toPct } from "../format";

interface EffortDatum {
  name: string;
  attempts: number;
  mastery: number;
  streak: number;
  color: string;
}

function toData(topics: TopicAnalyticsDTO[]): EffortDatum[] {
  return topics.map((t) => ({
    name: t.concept_name,
    attempts: t.attempts,
    mastery: toPct(t.mastery),
    streak: t.streak,
    color: toneColor[safeTone(t.tone)],
  }));
}

function EffortTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: EffortDatum }[];
}) {
  if (!active || !payload?.length) return null;
  const d = payload[0]!.payload;
  return (
    <div style={{ ...TOOLTIP_STYLE, padding: "8px 10px" }}>
      <div style={{ fontWeight: 700 }}>{d.name}</div>
      <div style={{ color: CHART.ink2 }}>
        {d.attempts} attempts · {d.mastery}% mastery · streak {d.streak}
      </div>
    </div>
  );
}

/** Effort (attempts) vs mastery; big low-mastery bubbles = lots of practice, little to show. */
export function EffortScatter({ topics }: { topics: TopicAnalyticsDTO[] }) {
  const data = toData(topics);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ScatterChart margin={{ top: 8, right: 14, bottom: 4, left: -18 }}>
        <CartesianGrid stroke={CHART.line} strokeDasharray="3 3" />
        <XAxis
          type="number"
          dataKey="attempts"
          name="Attempts"
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={false}
          allowDecimals={false}
        />
        <YAxis
          type="number"
          dataKey="mastery"
          name="Mastery"
          domain={[0, 100]}
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v: number) => `${v}%`}
        />
        <ZAxis type="number" dataKey="streak" range={[70, 420]} name="Streak" />
        <Tooltip content={<EffortTooltip />} cursor={{ stroke: CHART.line }} />
        <Scatter data={data} fillOpacity={0.75}>
          {data.map((d) => (
            <Cell key={d.name} fill={d.color} />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );
}
