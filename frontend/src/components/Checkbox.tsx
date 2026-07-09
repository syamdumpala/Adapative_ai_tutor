import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: ReactNode;
  id?: string;
  disabled?: boolean;
  /** Inline error shown beneath the row (also tints the box). */
  error?: string;
}

function Box({ checked, error }: { checked: boolean; error?: string }) {
  return (
    <span
      aria-hidden
      className={cn(
        "mt-[1px] grid h-[18px] w-[18px] flex-none place-items-center rounded-[6px] border text-[11px] text-white transition peer-focus-visible:ring-2 peer-focus-visible:ring-green-s",
        checked
          ? "border-green bg-green"
          : error
            ? "border-coral bg-card"
            : "border-line bg-card",
      )}
    >
      {checked && "✓"}
    </span>
  );
}

/** Accessible, controlled checkbox with a styled box and optional error. */
export function Checkbox({
  checked,
  onChange,
  label,
  id,
  disabled = false,
  error,
}: CheckboxProps) {
  const errorId = error && id ? `${id}-error` : undefined;
  return (
    <div>
      <label
        className={cn(
          "flex cursor-pointer items-start gap-[9px] text-[12.5px] text-ink2",
          disabled && "cursor-not-allowed opacity-60",
        )}
      >
        <input
          id={id}
          type="checkbox"
          checked={checked}
          disabled={disabled}
          aria-invalid={Boolean(error)}
          aria-describedby={errorId}
          onChange={(event) => onChange(event.target.checked)}
          className="peer sr-only"
        />
        <Box checked={checked} error={error} />
        <span>{label}</span>
      </label>
      {error && (
        <p
          id={errorId}
          className="mt-[6px] text-[11.5px] font-semibold text-coral-d"
        >
          {error}
        </p>
      )}
    </div>
  );
}
