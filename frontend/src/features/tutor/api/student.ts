import { apiGet, type Page, qs } from "@/lib/api";

/** Student-facing API client + mappers onto the existing view types. */

export interface ProfileDTO {
  full_name: string;
  initials: string;
  role_label: string;
  grade: string | null;
  email: string;
  member_since: string;
  subjects_available: number;
  avatar_gradient: string;
}

export interface PerfStatDTO {
  key: string;
  label: string;
  value: string;
  value_class: string;
}

export interface PerformanceDTO {
  recent_accuracy: string;
  concepts_mastered: number;
  day_streak: number;
  misconceptions_resolving: number;
  insight: {
    text: string;
    misconception: { name: string; status: string } | null;
  };
  stats: PerfStatDTO[];
}

export interface SessionDTO {
  id: string;
  subject_id: string | null;
  subject: { id: string; name: string; glyph: string; tone: string } | null;
  title: string;
  status: string;
  hint_rung: number;
  leak_checks: number;
  message_count: number;
  last_message: string | null;
  updated_at: string;
}

export interface MessageDTO {
  id: number;
  from: string;
  kind: string;
  text: string;
  created_at: string;
}

export function fetchProfile(): Promise<ProfileDTO> {
  return apiGet<ProfileDTO>("/me/profile");
}

export function fetchPerformance(): Promise<PerformanceDTO> {
  return apiGet<PerformanceDTO>("/me/performance");
}

export function fetchSessions(status?: string): Promise<Page<SessionDTO>> {
  return apiGet<Page<SessionDTO>>(
    `/tutor/sessions${qs({ status, sort: "-updated_at", limit: 100 })}`,
  );
}

export function fetchSessionMessages(
  sessionId: string,
): Promise<Page<MessageDTO>> {
  // 100 is the API's max page size; conversations in this app stay well under it.
  return apiGet<Page<MessageDTO>>(
    `/tutor/sessions/${encodeURIComponent(sessionId)}/messages${qs({ limit: 100 })}`,
  );
}
