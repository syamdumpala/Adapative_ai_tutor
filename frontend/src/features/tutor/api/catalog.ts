import { apiGet, apiPost, type Page, qs } from "@/lib/api";
import type { Tone } from "@/lib/tones";
import type { Topic } from "../types";

/**
 * Content-catalog API client + mappers.
 *
 * The backend still models these as "subjects" (`GET/POST /subjects`,
 * `subject_id`); the product surface calls them **topics**. This client is the
 * single place that bridges the two vocabularies.
 */

interface TopicDTO {
  id: string;
  name: string;
  glyph: string;
  tone: string;
  desc: string;
  meta: string;
  is_new: boolean;
  progress: number;
}

/** Fields a teacher supplies to create a topic (maps to the backend `SubjectCreate`). */
export interface TopicCreate {
  id: string;
  name: string;
  glyph: string;
  tone: Tone;
  desc: string;
  meta: string;
  is_new: boolean;
}

function toTopic(dto: TopicDTO): Topic {
  return {
    id: dto.id,
    name: dto.name,
    glyph: dto.glyph,
    tone: dto.tone as Tone,
    desc: dto.desc,
    meta: dto.meta,
    progress: dto.progress,
    isNew: dto.is_new,
  };
}

export async function fetchTopics(): Promise<Topic[]> {
  const page = await apiGet<Page<TopicDTO>>(`/subjects${qs({ limit: 100 })}`);
  return page.items.map(toTopic);
}

/** Create a new catalog topic (teacher only). POSTs to `/subjects`. */
export async function createTopic(payload: TopicCreate): Promise<Topic> {
  const dto = await apiPost<TopicDTO>("/subjects", payload);
  return toTopic(dto);
}
