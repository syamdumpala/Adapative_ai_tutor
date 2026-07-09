import { apiPost } from "@/lib/api";
import type { ChatMessage, ChatStatus, MessageSender } from "../types";
import type { ChatSummary } from "../state/chatHelpers";
import { fetchSessionMessages, fetchSessions } from "./student";

/** One tutor turn from `POST /tutor/ask`. */
export interface AskResult {
  session_id: string;
  action: string; // hint | evaluation | escalation | completed | diagnostic | await
  message: string;
  hint_level: number | null;
}

/** Send a student message to the live tutor graph. Omit `sessionId` to start one. */
export function askTutor(
  question: string,
  sessionId: string | null,
  topicId: string,
): Promise<AskResult> {
  return apiPost<AskResult>("/tutor/ask", {
    question,
    session_id: sessionId ?? undefined,
    subject_id: topicId,
  });
}

/** The graph's session status → the UI chat status. */
export function toChatStatus(action: string): ChatStatus {
  if (action === "completed") return "completed";
  return "pending";
}

/** Load the student's conversations for the "Your chats" rail. */
export async function fetchChatList(): Promise<{
  chats: Record<string, ChatSummary>;
  order: string[];
}> {
  const page = await fetchSessions();
  const chats: Record<string, ChatSummary> = {};
  for (const session of page.items) {
    chats[session.id] = {
      id: session.id,
      topicId: session.subject_id ?? "1",
      title: session.title,
      status: session.status as ChatStatus,
      hintRung: session.hint_rung,
    };
  }
  return { chats, order: page.items.map((s) => s.id) };
}

/** Load one conversation's full transcript. */
export async function fetchChatMessages(
  sessionId: string,
): Promise<ChatMessage[]> {
  const page = await fetchSessionMessages(sessionId);
  return page.items.map((message) => ({
    id: message.id,
    from: message.from as MessageSender,
    kind: "text",
    text: message.text,
  }));
}
