import {
  backendError,
  backendFetch,
  setSessionCookie,
  toAuthUser,
} from "@/server/backend";

/** Register a new account, then log it in so the user lands signed in. */
export async function POST(request: Request): Promise<Response> {
  const { name, email, password, role } = (await request.json()) as {
    name?: string;
    email?: string;
    password?: string;
    role?: "student" | "teacher";
  };
  if (!name || !email || !password) {
    return Response.json(
      { error: "Name, email and password are required." },
      { status: 400 },
    );
  }

  const register = await backendFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      student_name: name,
      email,
      password,
      role: role === "teacher" ? "teacher" : "student",
    }),
  });
  if (!register.ok) {
    return Response.json(
      { error: backendError(register.body, "Could not create the account.") },
      { status: register.status === 409 ? 409 : 400 },
    );
  }

  const login = await backendFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  const token = (login.body as { access_token: string }).access_token;
  await setSessionCookie(token);
  const me = await backendFetch("/auth/me", {}, token);
  return Response.json(toAuthUser(me.body), { status: 201 });
}
