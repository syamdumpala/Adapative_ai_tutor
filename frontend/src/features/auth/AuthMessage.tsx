import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface AuthMessageProps {
  tone: "error" | "note";
  children: ReactNode;
}

/** Inline error / confirmation banner for the auth form. */
export function AuthMessage({ tone, children }: AuthMessageProps) {
  const error = tone === "error";
  return (
    <div
      className={cn(
        "flex animate-fade-up items-start gap-[9px] rounded-sm px-[13px] py-[11px] text-[12.5px] font-semibold leading-[1.45]",
        error
          ? "border border-[rgba(233,96,60,0.35)] bg-coral-s text-coral-d"
          : "border border-green-s bg-green-s2 text-green-d",
      )}
    >
      <span
        className={cn(
          "mt-[1px] grid h-[17px] w-[17px] flex-none place-items-center rounded-full font-extrabold text-white",
          error ? "bg-coral text-[11px]" : "bg-green text-[10px]",
        )}
      >
        {error ? "!" : "✓"}
      </span>
      <span>{children}</span>
    </div>
  );
}
