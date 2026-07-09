import { cn } from "@/lib/cn";

interface ProgressBarProps {
  /** Fill fraction, 0–1. */
  value: number;
  /** Tailwind background utility for the fill (see `progressFillTone`). */
  fillClassName: string;
  /** Track height in pixels. */
  height?: number;
  /** Stagger the grow animation, in seconds. */
  delaySec?: number;
  className?: string;
}

function clamp01(value: number): number {
  return Math.max(0, Math.min(1, value));
}

/** Horizontal track with an animated, left-anchored fill. */
export function ProgressBar({
  value,
  fillClassName,
  height = 5,
  delaySec = 0,
  className,
}: ProgressBarProps) {
  const pct = Math.round(clamp01(value) * 100);
  return (
    <div
      style={{ height }}
      className={cn("overflow-hidden rounded-full bg-wash", className)}
    >
      <div
        style={{
          width: `${pct}%`,
          animation: `growX 0.8s cubic-bezier(0.2,0.7,0.3,1) ${delaySec}s both`,
        }}
        className={cn("h-full origin-left rounded-full", fillClassName)}
      />
    </div>
  );
}
