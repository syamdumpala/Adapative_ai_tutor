export type AuthMode = "signin" | "signup";
export type AuthRole = "student" | "teacher";

export interface SignInInput {
  email: string;
  password: string;
  remember: boolean;
}

export interface SignUpInput {
  name: string;
  email: string;
  password: string;
  confirm: string;
  role: AuthRole | null;
}

/** The authenticated user the backend will return once the API is wired. */
export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: AuthRole;
}

/** Per-field validation messages, keyed by the input's field name. */
export type FieldErrors<T> = Partial<Record<keyof T, string>>;
