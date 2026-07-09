"use client";

import { useMemo, useState } from "react";
import { EmptyState, SearchInput } from "@/components";
import { useTopics } from "../hooks/useTopics";
import type { Topic } from "../types";
import { ProfileMenu } from "./ProfileMenu";
import { TopicCard } from "./TopicCard";

interface TopicGridProps {
  name: string;
  initials: string;
  onOpenTopic: (id: string) => void;
  onProfile: () => void;
  onPerformance: () => void;
  onAnalytics: () => void;
  onLogout: () => void;
}

type MenuProps = Pick<
  TopicGridProps,
  | "name"
  | "initials"
  | "onProfile"
  | "onPerformance"
  | "onAnalytics"
  | "onLogout"
>;

/** Case-insensitive match of a topic against a search needle (name + blurb). */
function matchesQuery(topic: Topic, needle: string): boolean {
  return (
    topic.name.toLowerCase().includes(needle) ||
    topic.desc.toLowerCase().includes(needle)
  );
}

function TopicGridHeader({
  name,
  initials,
  onProfile,
  onPerformance,
  onAnalytics,
  onLogout,
}: MenuProps) {
  return (
    <div className="mb-[clamp(14px,2vw,22px)] flex animate-fade-up flex-wrap items-start justify-between gap-4">
      <div className="min-w-0">
        <div className="mb-[9px] font-mono text-[10px] uppercase tracking-[0.14em] text-ink3">
          Topics
        </div>
        <h1 className="text-[clamp(25px,4vw,38px)] font-extrabold">
          Hi, {name}. Pick a topic to begin.
        </h1>
        <p className="mt-2 max-w-[48ch] text-[14px] text-ink2">
          Open any topic and just ask — Mira guides you with hints, never
          straight answers.
        </p>
      </div>
      <ProfileMenu
        name={name}
        initials={initials}
        onProfile={onProfile}
        onPerformance={onPerformance}
        onAnalytics={onAnalytics}
        onLogout={onLogout}
      />
    </div>
  );
}

function TopicResults({
  topics,
  query,
  onOpenTopic,
}: {
  topics: Topic[];
  query: string;
  onOpenTopic: (id: string) => void;
}) {
  if (topics.length === 0) {
    return (
      <EmptyState size="lg">
        No topics match “{query.trim()}”. Try a different search.
      </EmptyState>
    );
  }
  return (
    <div className="grid gap-[clamp(12px,1.6vw,18px)] [grid-template-columns:repeat(auto-fill,minmax(min(100%,240px),1fr))]">
      {topics.map((topic) => (
        <TopicCard
          key={topic.id}
          topic={topic}
          onClick={() => onOpenTopic(topic.id)}
        />
      ))}
    </div>
  );
}

/** Topics header (greeting + account menu) over a searchable topic card grid. */
export function TopicGrid({
  name,
  initials,
  onOpenTopic,
  onProfile,
  onPerformance,
  onAnalytics,
  onLogout,
}: TopicGridProps) {
  const topics = useTopics();
  const [query, setQuery] = useState("");
  const needle = query.trim().toLowerCase();
  const filtered = useMemo(
    () =>
      needle ? topics.filter((topic) => matchesQuery(topic, needle)) : topics,
    [topics, needle],
  );

  return (
    <>
      <TopicGridHeader
        name={name}
        initials={initials}
        onProfile={onProfile}
        onPerformance={onPerformance}
        onAnalytics={onAnalytics}
        onLogout={onLogout}
      />
      <SearchInput
        value={query}
        onChange={setQuery}
        placeholder="Search topics…"
        className="mb-[clamp(14px,1.8vw,22px)] max-w-[380px] animate-fade-up"
      />
      <TopicResults topics={filtered} query={query} onOpenTopic={onOpenTopic} />
    </>
  );
}
