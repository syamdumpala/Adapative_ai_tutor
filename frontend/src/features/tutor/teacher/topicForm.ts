import { useState } from "react";
import { ApiError } from "@/lib/api";
import type { Tone } from "@/lib/tones";
import { createTopic, type TopicCreate } from "../api/catalog";
import type { Topic } from "../types";

/** Editable state of the create-topic form. */
export interface Draft {
  name: string;
  glyph: string;
  tone: Tone;
  desc: string;
  meta: string;
  isNew: boolean;
}

export const EMPTY_DRAFT: Draft = {
  name: "",
  glyph: "",
  tone: "green",
  desc: "",
  meta: "",
  isNew: true,
};

/** Slugify a name into a backend-safe id (`^[a-z0-9_-]+$`). */
export function slugify(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/** The glyph to show/send: the typed one, else the name's first letter. */
export function glyphFor(draft: Draft): string {
  return draft.glyph.trim() || draft.name.trim().charAt(0).toUpperCase() || "?";
}

// Backend caps (SubjectCreate): id≤64, name≤128, glyph≤16, desc≤255, meta≤64.
function buildPayload(
  draft: Draft,
  existingTopics: Topic[],
): { payload?: TopicCreate; error?: string } {
  const name = draft.name.trim();
  // Ids are decoupled from names (seeds use "1".."6"), so dedupe on the name a
  // student actually sees, plus the derived id, and clamp the slug to 64 chars.
  const id = slugify(name).slice(0, 64);
  if (!id) return { error: "Enter a topic name." };
  if (name.length > 128)
    return { error: "Please use a shorter topic name (128 characters max)." };
  const clash = existingTopics.some(
    (t) => t.id === id || t.name.trim().toLowerCase() === name.toLowerCase(),
  );
  if (clash) return { error: "A topic with this name already exists." };
  return {
    payload: {
      id,
      name,
      glyph: glyphFor(draft).slice(0, 16),
      tone: draft.tone,
      desc: draft.desc.trim().slice(0, 255),
      meta: draft.meta.trim().slice(0, 64),
      is_new: draft.isNew,
    },
  };
}

/** Map a failed create into an actionable message. */
function submitError(err: unknown): string {
  if (err instanceof ApiError && err.status === 409)
    return "A topic with this id already exists.";
  if (err instanceof ApiError && err.status === 422)
    return "Some details are too long — please shorten them.";
  return "Couldn't create the topic. Please try again.";
}

export interface TopicForm {
  draft: Draft;
  submitting: boolean;
  error: string | null;
  patch: (part: Partial<Draft>) => void;
  reset: () => void;
  submit: () => Promise<void>;
}

/** Controlled create-topic form: validation, submit to `/subjects`, errors. */
export function useTopicForm(
  existingTopics: Topic[],
  onCreated: (topic: Topic) => void,
): TopicForm {
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const patch = (part: Partial<Draft>) =>
    setDraft((prev) => ({ ...prev, ...part }));
  const reset = () => {
    setDraft(EMPTY_DRAFT);
    setError(null);
  };

  const submit = async () => {
    const { payload, error: invalid } = buildPayload(draft, existingTopics);
    if (!payload) {
      setError(invalid ?? "Please check the form.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      onCreated(await createTopic(payload));
      setDraft(EMPTY_DRAFT);
    } catch (err) {
      setError(submitError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return { draft, submitting, error, patch, reset, submit };
}
