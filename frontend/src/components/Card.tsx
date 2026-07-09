import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";

/**
 * The shared surface treatment (white card, hairline border, soft shadow).
 * Callers add radius / padding / hover behaviour via `className`.
 */
export function Card({
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("border border-line bg-card shadow-soft", className)}
      {...rest}
    >
      {children}
    </div>
  );
}
