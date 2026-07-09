import type { ReactNode } from "react";
import { Card, EmptyState } from "@/components";
import { InfoDot } from "./InfoDot";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  /** Optional "?" help paragraph shown on hover next to the title. */
  info?: string;
  /** Fixed height (px) for the chart body; keeps ResponsiveContainer measurable. */
  height?: number;
  /** When true, show the empty message instead of the chart. */
  isEmpty?: boolean;
  emptyMessage?: string;
  children: ReactNode;
}

/** Titled surface wrapping one chart, with a graceful empty state. */
export function ChartCard({
  title,
  subtitle,
  info,
  height = 240,
  isEmpty = false,
  emptyMessage = "No data yet — complete a few sessions to see this chart.",
  children,
}: ChartCardProps) {
  return (
    <Card className="flex animate-fade-up flex-col rounded-md p-[clamp(14px,1.8vw,20px)]">
      <div className="mb-1">
        <div className="flex items-center gap-[6px]">
          <h3 className="text-[14px] font-bold text-ink">{title}</h3>
          {info && <InfoDot text={info} />}
        </div>
        {subtitle && (
          <p className="mt-[2px] text-[12px] text-ink2">{subtitle}</p>
        )}
      </div>
      {isEmpty ? (
        <div
          className="flex flex-1 items-center justify-center"
          style={{ height }}
        >
          <EmptyState size="sm">{emptyMessage}</EmptyState>
        </div>
      ) : (
        <div className="mt-2 w-full" style={{ height }}>
          {children}
        </div>
      )}
    </Card>
  );
}
