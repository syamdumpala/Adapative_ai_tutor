import type { AuthUser, SignInInput, SignUpInput } from "./types";

/**
 * Auth API client — talks to the same-origin BFF route handlers
 * (`/api/auth/*`), never the backend directly, so the JWT stays in an httpOnly
 * cookie and off the client bundle (see `docs/security/SECURITY.md`).
 */

/** Thrown when an auth request fails; carries a user-facing message. */
export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AuthError";
  }
}

/** Retained for backwards compatibility with existing error handling. */
export class AuthNotConnectedError extends AuthError {
  constructor() {
    super("Authentication is not connected to the server yet.");
    this.name = "AuthNotConnectedError";
  }
}

async function post(path: string, body: unknown): Promise<AuthUser> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "same-origin",
  });
  const data: unknown = await res.json().catch(() => null);
  if (!res.ok) {
    const message =
      (data as { error?: string } | null)?.error ?? "Something went wrong.";
    throw new AuthError(message);
  }
  return data as AuthUser;
}

export async function signIn(input: SignInInput): Promise<AuthUser> {
  return post("/api/auth/login", {
    email: input.email,
    password: input.password,
  });
}

export async function signUp(input: SignUpInput): Promise<AuthUser> {
  return post("/api/auth/register", {
    name: input.name,
    email: input.email,
    password: input.password,
    role: input.role ?? "student",
  });
}

export async function signOut(): Promise<void> {
  await fetch("/api/auth/logout", {
    method: "POST",
    credentials: "same-origin",
  });
}

export async function requestPasswordReset(email: string): Promise<void> {
  void email; // TODO(api): backend has no password-reset endpoint yet.
  throw new AuthError("Password reset isn't available yet.");
}
