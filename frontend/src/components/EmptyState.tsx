import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface EmptyStateProps {
  children: ReactNode;
  /** `lg` for primary empty views; `sm` for inline "no results". */
  size?: "sm" | "lg";
  className?: string;
}

/** Dashed-border placeholder for empty lists and no-match search results. */
export function EmptyState({
  children,
  size = "sm",
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "border border-dashed border-line bg-card text-center text-ink2",
        size === "lg"
          ? "rounded-lg p-6 text-[13px]"
          : "rounded-md p-5 text-[12.5px]",
        className,
      )}
    >
      {children}
    </div>
  );
}
