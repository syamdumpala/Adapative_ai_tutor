import { cn } from "@/lib/cn";

interface SegmentOption<T extends string> {
  value: T;
  label: string;
}

interface SegmentedControlProps<T extends string> {
  options: SegmentOption<T>[];
  value: T;
  onChange: (value: T) => void;
  /** `ink` = solid ink active pill; `card` = raised card active pill (forms). */
  variant?: "ink" | "card";
  /** Stretch segments to fill the track (equal widths). */
  stretch?: boolean;
  className?: string;
}

function segmentClass(variant: "ink" | "card", active: boolean): string {
  if (variant === "card") {
    return active
      ? "border border-line bg-card px-3 py-[9px] text-[13px] font-bold text-ink shadow-soft"
      : "border border-transparent bg-transparent px-3 py-[9px] text-[13px] font-semibold text-ink2";
  }
  return active
    ? "h-[34px] bg-ink px-5 text-[13.5px] font-bold text-paper shadow-soft"
    : "h-[34px] bg-transparent px-5 text-[13.5px] font-bold text-ink2";
}

/** Pill toggle for a small, mutually exclusive set (roles, auth modes). */
export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  variant = "ink",
  stretch = false,
  className,
}: SegmentedControlProps<T>) {
  return (
    <div
      className={cn(
        "gap-[3px] rounded-full border border-line bg-paper2 p-[4px] shadow-[inset_0_1px_2px_rgba(35,32,25,0.04)]",
        stretch ? "flex w-full" : "inline-flex",
        className,
      )}
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={cn(
            "rounded-full transition",
            stretch && "flex-1",
            segmentClass(variant, option.value === value),
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
