import { Fragment, type ReactNode } from "react";
import { cn } from "@/lib/cn";
import type { DiagnosisData } from "../../types";

const TRAIL: { name: string; gap?: boolean }[] = [
  { name: "Comparing fractions" },
  { name: "Comparing unit fractions" },
  { name: "Unit fractions" },
  { name: "Equal partitioning", gap: true },
];

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <>
      <span className="text-ink3">{label}</span>
      <span>{children}</span>
    </>
  );
}

function PrereqTrail() {
  return (
    <div className="border-t border-line pt-3">
      <div className="mb-[9px] font-mono text-[9px] uppercase tracking-[0.1em] text-ink3">
        Prerequisite trail · walking to the real gap
      </div>
      <div className="flex flex-wrap items-center gap-[6px]">
        {TRAIL.map((step, index) => (
          <Fragment key={step.name}>
            <span
              className={cn(
                "rounded-full px-[10px] py-[5px] text-[11.5px] font-semibold",
                step.gap
                  ? "bg-coral text-white shadow-[0_0_0_3px_var(--color-coral-s)]"
                  : "border border-line bg-paper2 text-ink2",
              )}
            >
              {step.name}
            </span>
            {index < TRAIL.length - 1 && (
              <span className="text-[13px] text-ink3">→</span>
            )}
          </Fragment>
        ))}
      </div>
    </div>
  );
}

/** Structured "diagnosis" output plus the prerequisite trail to the real gap. */
export function DiagnosisCard({ data }: { data: DiagnosisData }) {
  return (
    <div className="flex flex-col gap-[14px]">
      <div className="flex items-center gap-[9px]">
        <span className="grid h-[26px] w-[26px] place-items-center rounded-[8px] bg-coral-s text-[14px] text-coral-d">
          ⚑
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-coral-d">
          Diagnosis · structured output
        </span>
      </div>
      <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-[13px]">
        <Row label="error_class">
          <span className="font-bold text-coral-d">{data.err}</span>
        </Row>
        <Row label="misconception">
          <span className="font-mono font-bold">
            {data.misc} · {data.name}
          </span>
        </Row>
        <Row label="prerequisite_gap">
          <span className="font-bold text-ink">{data.prereq}</span>
        </Row>
        <Row label="evidence">
          <span className="italic text-ink2">{data.quote}</span>
        </Row>
      </div>
      <PrereqTrail />
    </div>
  );
}
