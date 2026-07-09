import { cn } from "@/lib/cn";

interface StatCardProps {
  value: string | number;
  label: string;
  /** `lg` = 26px figure (dashboards); `md` = 24px (compact panels). */
  size?: "md" | "lg";
  /** Card fill when not accented. */
  background?: "card" | "paper2";
  /** Highlight as a positive/hero stat (green wash). */
  accent?: boolean;
  /** Override the figure colour (ignored when `accent`). */
  valueClassName?: string;
}

/** Big figure over a caption — the KPI tile used in dashboards and modals. */
export function StatCard({
  value,
  label,
  size = "lg",
  background = "card",
  accent = false,
  valueClassName,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "rounded-md border p-[16px] shadow-soft",
        accent
          ? "border-green-s bg-green-s2"
          : cn(
              "border-line",
              background === "paper2" ? "bg-paper2" : "bg-card",
            ),
      )}
    >
      <div
        className={cn(
          "font-display font-extrabold leading-none",
          size === "lg" ? "text-[26px]" : "text-[24px]",
          accent ? "text-green-d" : "text-ink",
          !accent && valueClassName,
        )}
      >
        {value}
      </div>
      <div
        className={cn(
          "mt-[6px] text-[12px]",
          accent ? "text-green-d" : "text-ink2",
        )}
      >
        {label}
      </div>
    </div>
  );
}
