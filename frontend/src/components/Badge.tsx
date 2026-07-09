import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

export type BadgeTone =
  "neutral" | "green" | "amber" | "amberSolid" | "coral" | "violet" | "plain";

interface BadgeProps {
  /** Preset colour, or `plain` to supply colours through `className`. */
  tone?: BadgeTone;
  /** Monospace, uppercase, wider tracking (structured-output / meta chips). */
  mono?: boolean;
  /** Attention pulse (pending items). */
  pulse?: boolean;
  className?: string;
  children: ReactNode;
}

const toneClass: Record<Exclude<BadgeTone, "plain">, string> = {
  neutral: "border border-line bg-paper2 text-ink3",
  green: "bg-green-s text-green-d",
  amber: "bg-amber-s text-amber",
  amberSolid: "bg-amber text-white",
  coral: "bg-coral-s text-coral-d",
  violet: "bg-violet-s text-violet-d",
};

/** Small rounded status/label pill. */
export function Badge({
  tone = "neutral",
  mono = false,
  pulse = false,
  className,
  children,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center whitespace-nowrap rounded-full px-[10px] py-[3px] text-[10px] font-bold",
        mono ? "font-mono uppercase tracking-[0.1em]" : "tracking-[0.04em]",
        tone !== "plain" && toneClass[tone],
        pulse && "animate-pulse-amber",
        className,
      )}
    >
      {children}
    </span>
  );
}
