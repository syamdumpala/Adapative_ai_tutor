"use client";

import { signIn } from "./api";
import { AuthMessage } from "./AuthMessage";
import { AuthSubmit } from "./AuthSubmit";
import { SignInFields } from "./SignInFields";
import type { AuthUser, SignInInput } from "./types";
import { useAuthForm } from "./useAuthForm";
import { validateSignIn } from "./validation";

/** Email + password sign-in. */
export function SignInForm({
  onAuthed,
}: {
  onAuthed: (user: AuthUser) => void;
}) {
  const form = useAuthForm<SignInInput>({
    initial: { email: "", password: "", remember: true },
    validate: validateSignIn,
    onSubmit: async (values) => onAuthed(await signIn(values)),
  });

  return (
    <form
      onSubmit={form.handleSubmit}
      noValidate
      className="flex flex-col gap-[14px]"
    >
      <SignInFields form={form} />
      {form.formError && (
        <AuthMessage tone="error">{form.formError}</AuthMessage>
      )}
      {form.formNotice && (
        <AuthMessage tone="note">{form.formNotice}</AuthMessage>
      )}
      <AuthSubmit
        submitting={form.submitting}
        idle="Sign in"
        busy="Signing in…"
      />
    </form>
  );
}
