import {
  backendFetch,
  clearSessionCookie,
  readToken,
  toAuthUser,
} from "@/server/backend";

/** Return the currently signed-in user, or 401 if there is no valid session. */
export async function GET(): Promise<Response> {
  const token = await readToken();
  if (!token) {
    return Response.json({ error: "Not authenticated." }, { status: 401 });
  }
  const me = await backendFetch("/auth/me", {}, token);
  if (!me.ok) {
    await clearSessionCookie();
    return Response.json({ error: "Session expired." }, { status: 401 });
  }
  return Response.json(toAuthUser(me.body));
}
