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

/** One completed-session snapshot — a single point on the overall trend charts. */
export interface AnalyticsPointDTO {
  session_id: string;
  subject_id: string | null;
  subject_name: string | null;
  mastery: number;
  confidence: number;
  misconception_category: string | null;
  created_at: string | null;
}

/** Per-subject mean mastery & confidence across the subject's sessions. */
export interface SubjectAnalyticsDTO {
  subject_id: string | null;
  subject_name: string | null;
  mastery: number;
  confidence: number;
  sessions: number;
}

export interface AnalyticsDTO {
  by_subject: SubjectAnalyticsDTO[];
  points: AnalyticsPointDTO[];
}

/** One concept the student has engaged with — a point on the per-topic charts. */
export interface TopicAnalyticsDTO {
  concept_id: string;
  concept_name: string;
  subject_id: string | null;
  subject_name: string | null;
  glyph: string;
  tone: string;
  difficulty_band: string;
  mastery: number;
  confidence: number;
  understanding: string;
  attempts: number;
  streak: number;
  last_seen: string | null;
  next_review: string | null;
}

export interface TopicAnalyticsResponseDTO {
  topics: TopicAnalyticsDTO[];
}

export function fetchProfile(): Promise<ProfileDTO> {
  return apiGet<ProfileDTO>("/me/profile");
}

export function fetchAnalytics(): Promise<AnalyticsDTO> {
  return apiGet<AnalyticsDTO>("/me/analytics");
}

export function fetchTopicAnalytics(): Promise<TopicAnalyticsResponseDTO> {
  return apiGet<TopicAnalyticsResponseDTO>("/me/topics");
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
