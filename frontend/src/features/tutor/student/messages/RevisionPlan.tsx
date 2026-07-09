import { cn } from "@/lib/cn";

const ITEMS: { when: string; text: string; done?: boolean }[] = [
  { when: "Today", text: "Equal partitioning — rebuilt ✓", done: true },
  { when: "in 2 days", text: "Comparing unit fractions — quick check" },
  { when: "in 5 days", text: "Comparing any fractions" },
];

/** Spaced-repetition revision schedule shown when a session wraps up. */
export function RevisionPlan() {
  return (
    <div className="flex flex-col gap-[12px]">
      <div className="flex items-center gap-[9px]">
        <span className="grid h-[26px] w-[26px] place-items-center rounded-[8px] bg-amber-s text-[14px] text-amber">
          ◷
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-amber">
          Revision plan · spaced repetition
        </span>
      </div>
      <div className="flex flex-col gap-[8px]">
        {ITEMS.map((item) => (
          <div
            key={item.when}
            className="flex items-center gap-[11px] rounded-sm border border-line bg-paper2 px-[12px] py-[10px]"
          >
            <span
              className={cn(
                "flex-none rounded-[8px] px-[9px] py-1 font-mono text-[9.5px] uppercase tracking-[0.04em]",
                item.done ? "bg-green text-white" : "bg-amber-s text-amber",
              )}
            >
              {item.when}
            </span>
            <span className="flex-1 text-[13px] font-semibold text-ink">
              {item.text}
            </span>
            {item.done && (
              <span className="font-extrabold text-green-d">✓</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
