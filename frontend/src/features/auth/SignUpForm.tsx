"use client";

import { signUp } from "./api";
import { AuthMessage } from "./AuthMessage";
import { AuthSubmit } from "./AuthSubmit";
import { SignUpFields } from "./SignUpFields";
import type { AuthRole, AuthUser, SignUpInput } from "./types";
import { useAuthForm } from "./useAuthForm";
import { validateSignUp } from "./validation";

interface SignUpFormProps {
  onAuthed: (user: AuthUser) => void;
  defaultRole?: AuthRole | null;
}

/** Name + email + password (with confirm) + role account creation. */
export function SignUpForm({ onAuthed, defaultRole = null }: SignUpFormProps) {
  const form = useAuthForm<SignUpInput>({
    initial: {
      name: "",
      email: "",
      password: "",
      confirm: "",
      role: defaultRole,
    },
    validate: validateSignUp,
    onSubmit: async (values) => onAuthed(await signUp(values)),
  });

  return (
    <form
      onSubmit={form.handleSubmit}
      noValidate
      className="flex flex-col gap-[14px]"
    >
      <SignUpFields form={form} />
      {form.formError && (
        <AuthMessage tone="error">{form.formError}</AuthMessage>
      )}
      {form.formNotice && (
        <AuthMessage tone="note">{form.formNotice}</AuthMessage>
      )}
      <AuthSubmit
        submitting={form.submitting}
        idle="Create account"
        busy="Creating your account…"
      />
    </form>
  );
}
