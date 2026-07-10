import { apiGet, apiPost, type Page, qs } from "@/lib/api";
import type { Health, Understanding } from "@/lib/tones";
import type { AnalyticsDTO, PerformanceDTO } from "./student";
import type { Engagement, TeacherStudent } from "../data/teacher";

/** A specific student's overall analytics / KPIs (teacher view; same shape as `/me/*`). */
export function fetchStudentAnalytics(id: string): Promise<AnalyticsDTO> {
  return apiGet<AnalyticsDTO>(
    `/teacher/students/${encodeURIComponent(id)}/analytics`,
  );
}

export function fetchStudentPerformance(id: string): Promise<PerformanceDTO> {
  return apiGet<PerformanceDTO>(
    `/teacher/students/${encodeURIComponent(id)}/performance`,
  );
}

/** Teacher-dashboard API client + mappers onto the existing view types. */

interface RosterDTO {
  id: string;
  name: string;
  initials: string;
  tone: string;
  status: string;
  improvement: string;
  topics_explored: number;
}

interface EngagementDTO {
  asked: number;
  u: string;
  m: number;
}

interface ExploredTopicDTO {
  topic: { id: string };
  engagement: EngagementDTO;
}

export interface EscalationDTO {
  id: number;
  student_id: string;
  student_name: string;
  session_id: string;
  trigger: string | null;
  reason: string;
  excerpt: string | null;
  status: string;
  created_at: string;
}

function toEngagement(dto: EngagementDTO): Engagement {
  return { asked: dto.asked, u: dto.u as Understanding, m: dto.m };
}

async function fetchStudentEng(
  id: string,
): Promise<Record<string, Engagement>> {
  const topics = await apiGet<Page<ExploredTopicDTO>>(
    `/teacher/students/${encodeURIComponent(id)}/topics${qs({ limit: 100 })}`,
  );
  const eng: Record<string, Engagement> = {};
  for (const item of topics.items)
    eng[item.topic.id] = toEngagement(item.engagement);
  return eng;
}

/**
 * Build the roster in the shape the dashboard components already consume,
 * assembling each student's per-topic engagement from the split endpoints.
 * `query` is applied server-side against name/email.
 */
export async function fetchRoster(query?: string): Promise<TeacherStudent[]> {
  const roster = await apiGet<Page<RosterDTO>>(
    `/teacher/students${qs({ q: query, limit: 100 })}`,
  );
  return Promise.all(
    roster.items.map(async (row) => ({
      id: row.id,
      name: row.name,
      initials: row.initials,
      tone: row.tone as Health,
      status: row.status,
      improvement: row.improvement,
      eng: await fetchStudentEng(row.id),
    })),
  );
}

export function fetchEscalations(
  status?: string,
): Promise<Page<EscalationDTO>> {
  return apiGet<Page<EscalationDTO>>(
    `/teacher/escalations${qs({ status, limit: 100 })}`,
  );
}

export function resolveEscalation(
  id: number,
  notes?: string,
): Promise<EscalationDTO> {
  return apiPost<EscalationDTO>(`/teacher/escalations/${id}/resolve`, {
    teacher_notes: notes ?? null,
  });
}

export interface SimulateDayResult {
  advanced: number;
  message: string;
}

export function simulateDay(): Promise<SimulateDayResult> {
  return apiPost<SimulateDayResult>("/teacher/simulate-day");
}
