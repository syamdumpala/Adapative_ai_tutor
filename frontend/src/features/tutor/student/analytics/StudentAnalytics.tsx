"use client";

import { useState } from "react";
import { SegmentedControl } from "@/components";
import { OverviewPanel } from "./OverviewPanel";
import { TopicsPanel } from "./TopicsPanel";

type Tab = "overview" | "topics";

const TABS: { value: Tab; label: string }[] = [
  { value: "overview", label: "Overall" },
  { value: "topics", label: "By topic" },
];

function AnalyticsHeader({
  name,
  tab,
  onTab,
  onBack,
}: {
  name: string;
  tab: Tab;
  onTab: (t: Tab) => void;
  onBack: () => void;
}) {
  return (
    <div className="mb-[clamp(14px,2vw,22px)] flex animate-fade-up flex-wrap items-center justify-between gap-4">
      <div className="min-w-0">
        <button
          type="button"
          onClick={onBack}
          className="mb-[9px] flex items-center gap-[6px] rounded-full border border-line bg-card px-[12px] py-[6px] text-[12px] font-semibold text-ink2 shadow-soft transition hover:border-line2"
        >
          <span aria-hidden>←</span> Home
        </button>
        <h1 className="text-[clamp(22px,3.4vw,32px)] font-extrabold">
          {name}&apos;s progress
        </h1>
        <p className="mt-1 max-w-[52ch] text-[13.5px] text-ink2">
          How your mastery, confidence and misconceptions are trending across
          every session and topic.
        </p>
      </div>
      <SegmentedControl options={TABS} value={tab} onChange={onTab} />
    </div>
  );
}

/** Dedicated student analytics page: overall trends + per-topic breakdowns. */
export function StudentAnalytics({
  name,
  onBack,
}: {
  name: string;
  onBack: () => void;
}) {
  const [tab, setTab] = useState<Tab>("overview");
  return (
    <main
      className="scrolly min-h-0 flex-1 overflow-auto p-[clamp(20px,3vw,40px)]"
      data-screen="student-analytics"
    >
      <div className="mx-auto max-w-[1080px]">
        <AnalyticsHeader name={name} tab={tab} onTab={setTab} onBack={onBack} />
        {tab === "overview" ? <OverviewPanel /> : <TopicsPanel />}
      </div>
    </main>
  );
}
