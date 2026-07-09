import type { AuthUser, SignInInput, SignUpInput } from "./types";

/**
 * Auth API client — the single seam where the backend gets wired in.
 *
 * Nothing here talks to a server yet (by design). When the API is ready, replace
 * each body with a call to a **server-side route handler** (e.g. `/api/auth/*`)
 * so credentials/tokens never sit in the client bundle — see
 * `docs/security/SECURITY.md`. Keep the function signatures stable; the forms
 * already `await` them and handle success, field errors, and failures.
 */

/** Thrown by the placeholder client until the auth API is connected. */
export class AuthNotConnectedError extends Error {
  constructor() {
    super("Authentication is not connected to the server yet.");
    this.name = "AuthNotConnectedError";
  }
}

export async function signIn(input: SignInInput): Promise<AuthUser> {
  void input; // TODO(api): POST credentials to the auth route; return the session user.
  throw new AuthNotConnectedError();
}

export async function signUp(input: SignUpInput): Promise<AuthUser> {
  void input; // TODO(api): POST the new account to the auth route; return the session user.
  throw new AuthNotConnectedError();
}

export async function requestPasswordReset(email: string): Promise<void> {
  void email; // TODO(api): POST the email to the password-reset route.
  throw new AuthNotConnectedError();
}
