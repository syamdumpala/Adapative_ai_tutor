import {
  backendError,
  backendFetch,
  setSessionCookie,
  toAuthUser,
} from "@/server/backend";

/** Log in: exchange credentials for a JWT, store it in an httpOnly cookie, return the user. */
export async function POST(request: Request): Promise<Response> {
  const { email, password } = (await request.json()) as {
    email?: string;
    password?: string;
  };
  if (!email || !password) {
    return Response.json(
      { error: "Email and password are required." },
      { status: 400 },
    );
  }

  const login = await backendFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (!login.ok) {
    return Response.json(
      { error: backendError(login.body, "Invalid email or password.") },
      { status: login.status === 401 ? 401 : 400 },
    );
  }

  const token = (login.body as { access_token: string }).access_token;
  await setSessionCookie(token);
  const me = await backendFetch("/auth/me", {}, token);
  return Response.json(toAuthUser(me.body));
}
