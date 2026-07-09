"use client";

import {
  Button,
  Checkbox,
  GlyphTile,
  Modal,
  SegmentedControl,
  TextField,
} from "@/components";
import type { Tone } from "@/lib/tones";
import type { Topic } from "../types";
import { type Draft, glyphFor, useTopicForm } from "./topicForm";

interface TopicCreateModalProps {
  open: boolean;
  onClose: () => void;
  existingTopics: Topic[];
  onCreated: (topic: Topic) => void;
}

type FieldProps = { draft: Draft; patch: (part: Partial<Draft>) => void };

const TONE_OPTIONS: { value: Tone; label: string }[] = [
  { value: "green", label: "Green" },
  { value: "violet", label: "Violet" },
  { value: "amber", label: "Amber" },
  { value: "coral", label: "Coral" },
];

function DraftPreview({ draft }: { draft: Draft }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-line bg-paper2 px-[14px] py-3">
      <GlyphTile glyph={glyphFor(draft)} tone={draft.tone} size={44} />
      <div className="min-w-0">
        <div className="truncate text-[15px] font-bold">
          {draft.name.trim() || "New topic"}
        </div>
        <div className="truncate text-[12px] text-ink2">
          {draft.desc.trim() || "Add a short description students will see."}
        </div>
      </div>
    </div>
  );
}

function PrimaryFields({ draft, patch }: FieldProps) {
  return (
    <>
      <TextField
        id="topic-name"
        label="Topic name"
        value={draft.name}
        onChange={(v) => patch({ name: v })}
        placeholder="e.g. Algebra Basics"
      />
      <TextField
        id="topic-desc"
        label="Description"
        value={draft.desc}
        onChange={(v) => patch({ desc: v })}
        placeholder="Compare, simplify, add & subtract"
      />
      <TextField
        id="topic-glyph"
        label="Glyph"
        value={draft.glyph}
        onChange={(v) => patch({ glyph: v })}
        hint="A short symbol for the card (½, %, △). Defaults to the first letter."
        placeholder="½"
      />
    </>
  );
}

function SecondaryFields({ draft, patch }: FieldProps) {
  return (
    <>
      <TextField
        id="topic-meta"
        label="Caption"
        value={draft.meta}
        onChange={(v) => patch({ meta: v })}
        hint="Small caption on the card, e.g. “6 concepts”."
        placeholder="6 concepts"
      />
      <div>
        <div className="mb-[6px] text-[12.5px] font-semibold text-ink2">
          Accent colour
        </div>
        <SegmentedControl
          variant="card"
          stretch
          options={TONE_OPTIONS}
          value={draft.tone}
          onChange={(v) => patch({ tone: v })}
        />
      </div>
      <Checkbox
        id="topic-new"
        checked={draft.isNew}
        onChange={(v) => patch({ isNew: v })}
        label="Mark as new (adds a “New” badge to the card)"
      />
    </>
  );
}

function Footer({
  onCancel,
  onSubmit,
  submitting,
}: {
  onCancel: () => void;
  onSubmit: () => void;
  submitting: boolean;
}) {
  return (
    <div className="flex justify-end gap-2">
      <Button variant="secondary" onClick={onCancel} disabled={submitting}>
        Cancel
      </Button>
      <Button variant="success" onClick={onSubmit} disabled={submitting}>
        {submitting ? "Creating…" : "Create topic"}
      </Button>
    </div>
  );
}

/** Create-topic dialog for teachers. On submit it POSTs to `/subjects`. */
export function TopicCreateModal({
  open,
  onClose,
  existingTopics,
  onCreated,
}: TopicCreateModalProps) {
  const { draft, submitting, error, patch, reset, submit } = useTopicForm(
    existingTopics,
    onCreated,
  );
  const close = () => {
    if (submitting) return;
    reset();
    onClose();
  };

  return (
    <Modal open={open} onClose={close} title="New topic" width={480}>
      <div className="flex flex-col gap-[14px] px-[18px] py-5">
        <DraftPreview draft={draft} />
        <div className="flex flex-col gap-[14px]">
          <PrimaryFields draft={draft} patch={patch} />
          <SecondaryFields draft={draft} patch={patch} />
        </div>
        {error && (
          <div
            role="alert"
            className="rounded-lg border border-coral-s bg-coral-s px-[13px] py-[10px] text-[12.5px] font-semibold text-coral-d"
          >
            {error}
          </div>
        )}
        <Footer
          onCancel={close}
          onSubmit={() => void submit()}
          submitting={submitting}
        />
      </div>
    </Modal>
  );
}
