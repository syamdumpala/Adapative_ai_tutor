import { backendFetch, readToken } from "@/server/backend";

/**
 * Authenticated pass-through to the FastAPI backend.
 *
 * The browser calls `/api/backend/<path>?<query>`; this handler attaches the
 * JWT from the httpOnly session cookie and forwards to the backend, so the
 * token never reaches client code. The backend remains the authority for
 * authorization (role guards, ownership), so a broad proxy is safe here.
 */
async function proxy(
  request: Request,
  ctx: { params: Promise<{ path: string[] }> },
): Promise<Response> {
  const { path } = await ctx.params;
  const token = await readToken();
  const search = new URL(request.url).search;
  const target = `/${path.map(encodeURIComponent).join("/")}${search}`;

  const method = request.method;
  const hasBody = method !== "GET" && method !== "HEAD" && method !== "DELETE";
  const body = hasBody ? await request.text() : undefined;

  const res = await backendFetch(
    target,
    { method, body: body || undefined },
    token,
  );
  return Response.json(res.body, { status: res.status });
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
