import { backendFetch, clearSessionCookie, readToken } from "@/server/backend";

/** Sign out: best-effort backend notify, then clear the session cookie. */
export async function POST(): Promise<Response> {
  const token = await readToken();
  if (token) {
    await backendFetch("/auth/logout", { method: "POST" }, token);
  }
  await clearSessionCookie();
  return new Response(null, { status: 204 });
}
