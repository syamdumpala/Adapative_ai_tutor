import type { FieldErrors, SignInInput, SignUpInput } from "./types";

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const MIN_PASSWORD = 8;

export function validateEmail(email: string): string | undefined {
  if (!email.trim()) return "Enter your email address.";
  if (!EMAIL.test(email.trim())) return "Enter a valid email address.";
  return undefined;
}

/** Signup password policy: length + a letter + a number. */
export function validatePassword(password: string): string | undefined {
  if (!password) return "Choose a password.";
  if (password.length < MIN_PASSWORD)
    return `Use at least ${MIN_PASSWORD} characters.`;
  if (!/[a-zA-Z]/.test(password) || !/[0-9]/.test(password))
    return "Include at least one letter and one number.";
  return undefined;
}

/** Live checklist shown under the signup password field. */
export function passwordRequirements(
  password: string,
): { label: string; met: boolean }[] {
  return [
    {
      label: `${MIN_PASSWORD}+ characters`,
      met: password.length >= MIN_PASSWORD,
    },
    { label: "a letter", met: /[a-zA-Z]/.test(password) },
    { label: "a number", met: /[0-9]/.test(password) },
  ];
}

function prune<T>(raw: Record<string, string | undefined>): FieldErrors<T> {
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(raw)) {
    if (value) out[key] = value;
  }
  return out as FieldErrors<T>;
}

export function validateSignIn(values: SignInInput): FieldErrors<SignInInput> {
  return prune<SignInInput>({
    email: validateEmail(values.email),
    password: values.password ? undefined : "Enter your password.",
  });
}

function confirmError(values: SignUpInput): string | undefined {
  if (!values.confirm) return "Re-enter your password.";
  if (values.confirm !== values.password) return "Passwords do not match.";
  return undefined;
}

export function validateSignUp(values: SignUpInput): FieldErrors<SignUpInput> {
  return prune<SignUpInput>({
    name: values.name.trim().length >= 2 ? undefined : "Enter your full name.",
    email: validateEmail(values.email),
    password: validatePassword(values.password),
    confirm: confirmError(values),
    role: values.role
      ? undefined
      : "Choose whether you're a student or a teacher.",
  });
}
