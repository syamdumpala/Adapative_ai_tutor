import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AnalyticsPointDTO } from "../../../api/student";
import {
  AXIS_TICK,
  CHART,
  CONFIDENCE_COLOR,
  MASTERY_COLOR,
  TOOLTIP_STYLE,
} from "../chartTheme";
import { shortDate, toPct } from "../format";

interface TrendDatum {
  label: string;
  mastery: number;
  confidence: number;
  flagged: boolean;
}

function toTrend(points: AnalyticsPointDTO[]): TrendDatum[] {
  return points.map((p, i) => ({
    label: shortDate(p.created_at, `#${i + 1}`),
    mastery: toPct(p.mastery),
    confidence: toPct(p.confidence),
    flagged: Boolean(p.misconception_category),
  }));
}

/** Coral ring on a mastery point where a misconception surfaced, else a plain dot. */
function TrendDot({
  cx,
  cy,
  payload,
}: {
  cx?: number;
  cy?: number;
  payload?: TrendDatum;
}) {
  if (cx === undefined || cy === undefined) return <circle r={0} />;
  const flagged = Boolean(payload?.flagged);
  return (
    <circle
      cx={cx}
      cy={cy}
      r={flagged ? 5.5 : 3}
      fill={flagged ? CHART.coral : MASTERY_COLOR}
      stroke="#fff"
      strokeWidth={flagged ? 2 : 1}
    />
  );
}

/** Mastery vs confidence across every completed session; coral dots flag misconceptions. */
export function MasteryTrendChart({ points }: { points: AnalyticsPointDTO[] }) {
  const data = toTrend(points);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart
        data={data}
        margin={{ top: 6, right: 10, bottom: 0, left: -18 }}
      >
        <CartesianGrid
          stroke={CHART.line}
          strokeDasharray="3 3"
          vertical={false}
        />
        <XAxis
          dataKey="label"
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          domain={[0, 100]}
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v: number) => `${v}%`}
        />
        <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => `${v}%`} />
        <Legend iconType="plainline" wrapperStyle={{ fontSize: 12 }} />
        <Line
          type="monotone"
          dataKey="mastery"
          name="Mastery"
          stroke={MASTERY_COLOR}
          strokeWidth={2.5}
          dot={<TrendDot />}
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="confidence"
          name="Confidence"
          stroke={CONFIDENCE_COLOR}
          strokeWidth={2}
          strokeDasharray="5 4"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
