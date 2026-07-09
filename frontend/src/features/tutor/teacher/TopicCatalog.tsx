"use client";

import { useEffect, useState } from "react";
import { Badge, Button, EmptyState, GlyphTile } from "@/components";
import { truncateWords } from "@/lib/text";
import { fetchTopics } from "../api/catalog";
import type { Topic } from "../types";
import { TopicCreateModal } from "./TopicCreateModal";

function CatalogCard({ topic }: { topic: Topic }) {
  return (
    <div className="flex min-h-[132px] flex-col rounded-lg border border-line bg-card p-[18px] shadow-soft">
      <div className="mb-[13px] flex items-start justify-between gap-[10px]">
        <GlyphTile glyph={topic.glyph} tone={topic.tone} size={44} />
        {topic.isNew && (
          <Badge tone="violet" mono className="text-[9px]">
            New
          </Badge>
        )}
      </div>
      <div className="font-display text-[17px] font-bold">{topic.name}</div>
      <div
        className="mt-[4px] flex-1 text-[12.5px] text-ink2"
        title={topic.desc}
      >
        {truncateWords(topic.desc, 5)}
      </div>
      {topic.meta && (
        <div className="mt-3 font-mono text-[10.5px] text-ink3">
          {topic.meta}
        </div>
      )}
    </div>
  );
}

function CatalogHeader({ onNew }: { onNew: () => void }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div className="min-w-0">
        <div className="mb-[6px] font-mono text-[10px] uppercase tracking-[0.14em] text-ink3">
          Catalog
        </div>
        <h1 className="text-[clamp(23px,3vw,31px)] font-extrabold">Topics</h1>
        <p className="mt-[7px] max-w-[62ch] text-[13.5px] text-ink2">
          The topics students see on their home screen. Add a new one and it
          appears for every student.
        </p>
      </div>
      <Button onClick={onNew}>
        <span className="text-[15px] leading-none">＋</span> New topic
      </Button>
    </div>
  );
}

function CatalogBody({
  loading,
  topics,
}: {
  loading: boolean;
  topics: Topic[];
}) {
  if (loading) return <EmptyState>Loading topics…</EmptyState>;
  if (topics.length === 0)
    return (
      <EmptyState size="lg">No topics yet — create the first one.</EmptyState>
    );
  return (
    <div className="grid gap-[clamp(12px,1.6vw,18px)] [grid-template-columns:repeat(auto-fill,minmax(min(100%,220px),1fr))]">
      {topics.map((topic) => (
        <CatalogCard key={topic.id} topic={topic} />
      ))}
    </div>
  );
}

/** Teacher topic catalog: live cards from `/subjects` + a create flow. */
export function TopicCatalog() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    let active = true;
    fetchTopics()
      .then((live) => active && setTopics(live))
      .catch(() => active && setTopics([]))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  const handleCreated = (topic: Topic) => {
    setTopics((prev) => [topic, ...prev.filter((t) => t.id !== topic.id)]);
    setModalOpen(false);
  };

  return (
    <div className="flex animate-fade-up flex-col gap-5">
      <CatalogHeader onNew={() => setModalOpen(true)} />
      <CatalogBody loading={loading} topics={topics} />
      <TopicCreateModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        existingTopics={topics}
        onCreated={handleCreated}
      />
    </div>
  );
}
