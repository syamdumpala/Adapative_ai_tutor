import { cookies } from "next/headers";

import type { AuthRole, AuthUser } from "@/features/auth/types";

/**
 * Server-only helpers for talking to the FastAPI backend.
 *
 * The browser never calls the backend directly — it hits our same-origin
 * `/api/*` route handlers, which read the JWT from an httpOnly cookie and
 * forward it here. That keeps the token out of the client bundle
 * (`docs/security/SECURITY.md`).
 */

export const SESSION_COOKIE = "mira_session";
const ONE_DAY_SECONDS = 60 * 60 * 24;

/** Base URL of the FastAPI backend as seen from the Next.js server (never the browser). */
export function backendBaseUrl(): string {
  return (
    process.env.API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:8000"
  );
}

/** Read the session JWT from the httpOnly cookie (or null if signed out). */
export async function readToken(): Promise<string | null> {
  const store = await cookies();
  return store.get(SESSION_COOKIE)?.value ?? null;
}

/** Persist the session JWT in an httpOnly, SameSite=Lax cookie. */
export async function setSessionCookie(token: string): Promise<void> {
  const store = await cookies();
  store.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: ONE_DAY_SECONDS,
  });
}

/** Remove the session cookie (sign out). */
export async function clearSessionCookie(): Promise<void> {
  const store = await cookies();
  store.delete(SESSION_COOKIE);
}

export interface BackendResponse {
  status: number;
  ok: boolean;
  body: unknown;
}

/** Call the backend and return its status + parsed JSON body (never throws on 4xx/5xx). */
export async function backendFetch(
  path: string,
  init: RequestInit = {},
  token?: string | null,
): Promise<BackendResponse> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${backendBaseUrl()}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  const text = await res.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  return { status: res.status, ok: res.ok, body };
}

/** Map the backend `/auth/me` payload onto the client-facing session user. */
export function toAuthUser(body: unknown): AuthUser {
  const u = (body ?? {}) as Record<string, unknown>;
  const role: AuthRole = u.role === "teacher" ? "teacher" : "student";
  return {
    id: String(u.id ?? ""),
    name: String(u.full_name ?? ""),
    email: String(u.email ?? ""),
    role,
  };
}

/** Pull a human-readable error message out of a FastAPI error body. */
export function backendError(body: unknown, fallback: string): string {
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string") return detail;
  return fallback;
}
