import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
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

const MI_COLOR = CHART.amber;
const MI_NAME = "Misconfidence";
const AXIS = { tick: AXIS_TICK, tickLine: false, axisLine: false } as const;
// Right axis always keeps 0 visible (neutral), padded around the data.
const MI_DOMAIN: [(min: number) => number, (max: number) => number] = [
  (min) => Math.min(-0.3, min - 0.05),
  (max) => Math.max(0.3, max + 0.05),
];

interface TrendDatum {
  label: string;
  mastery: number;
  confidence: number;
  mi: number;
  flagged: boolean;
}

function toTrend(points: AnalyticsPointDTO[]): TrendDatum[] {
  return points.map((p, i) => ({
    label: shortDate(p.created_at, `#${i + 1}`),
    mastery: toPct(p.mastery),
    confidence: toPct(p.confidence),
    mi: p.misconception_index,
    flagged: Boolean(p.misconception_category),
  }));
}

/** Coral ring on the index where a misconception surfaced, else a plain amber dot. */
function IndexDot({
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
      fill={flagged ? CHART.coral : MI_COLOR}
      stroke="#fff"
      strokeWidth={flagged ? 2 : 1}
    />
  );
}

type TipValue = number | string | ReadonlyArray<number | string> | undefined;
const fmt = (value: TipValue, name: number | string | undefined) =>
  name === MI_NAME ? Number(value).toFixed(2) : `${value}%`;

// Mastery + confidence on the left % axis; the signed index on the right axis.
const TREND_LINES = [
  <Line
    key="mastery"
    yAxisId="pct"
    type="monotone"
    dataKey="mastery"
    name="Mastery"
    stroke={MASTERY_COLOR}
    strokeWidth={2.2}
    dot={false}
  />,
  <Line
    key="confidence"
    yAxisId="pct"
    type="monotone"
    dataKey="confidence"
    name="Confidence"
    stroke={CONFIDENCE_COLOR}
    strokeWidth={2}
    strokeDasharray="5 4"
    dot={false}
  />,
  <Line
    key="mi"
    yAxisId="mi"
    type="monotone"
    dataKey="mi"
    name={MI_NAME}
    stroke={MI_COLOR}
    strokeWidth={2}
    dot={<IndexDot />}
    activeDot={{ r: 6 }}
  />,
];

/** Mastery, confidence and the signed Misconfidence Index across every completed session. */
export function MasteryTrendChart({ points }: { points: AnalyticsPointDTO[] }) {
  const data = toTrend(points);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart
        data={data}
        margin={{ top: 6, right: 4, bottom: 0, left: -18 }}
      >
        <CartesianGrid
          stroke={CHART.line}
          strokeDasharray="3 3"
          vertical={false}
        />
        <XAxis dataKey="label" {...AXIS} />
        <YAxis
          yAxisId="pct"
          domain={[0, 100]}
          {...AXIS}
          tickFormatter={(v) => `${v}%`}
        />
        <YAxis
          yAxisId="mi"
          orientation="right"
          domain={MI_DOMAIN}
          {...AXIS}
          tickFormatter={(v) => v.toFixed(1)}
        />
        <ReferenceLine
          yAxisId="mi"
          y={0}
          stroke={CHART.ink3}
          strokeDasharray="4 4"
        />
        <Tooltip contentStyle={TOOLTIP_STYLE} formatter={fmt} />
        <Legend iconType="plainline" wrapperStyle={{ fontSize: 12 }} />
        {TREND_LINES}
      </LineChart>
    </ResponsiveContainer>
  );
}
