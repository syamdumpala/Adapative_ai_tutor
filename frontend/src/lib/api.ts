/**
 * Browser-side API client.
 *
 * Every call goes to a same-origin `/api/backend/*` route handler (the BFF),
 * which attaches the session JWT from the httpOnly cookie and forwards to the
 * FastAPI backend. The token is never visible to this code.
 */

/** The pagination envelope every list endpoint returns. */
export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export class ApiError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const res = await fetch(`/api/backend${path}`, {
    method,
    headers:
      body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: "same-origin",
  });
  const data: unknown = await res.json().catch(() => null);
  if (!res.ok) {
    const record = data as { detail?: string; error?: string } | null;
    throw new ApiError(
      res.status,
      record?.detail ?? record?.error ?? `Request failed (${res.status})`,
    );
  }
  return data as T;
}

export const apiGet = <T>(path: string): Promise<T> => request<T>("GET", path);
export const apiPost = <T>(path: string, body?: unknown): Promise<T> =>
  request<T>("POST", path, body);
export const apiPatch = <T>(path: string, body?: unknown): Promise<T> =>
  request<T>("PATCH", path, body);

type QueryValue = string | number | boolean | undefined | null;

/** Build a `?a=1&b=2` query string, dropping empty values. */
export function qs(params: Record<string, QueryValue>): string {
  const sp = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "")
      sp.set(key, String(value));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}
