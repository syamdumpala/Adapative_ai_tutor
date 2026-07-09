import { LoginPage } from "@/features/auth/LoginPage";
import type { AuthMode, AuthRole } from "@/features/auth/types";

interface LoginRouteProps {
  searchParams: Promise<{ mode?: string; role?: string }>;
}

function asMode(value: string | undefined): AuthMode {
  return value === "signup" ? "signup" : "signin";
}

function asRole(value: string | undefined): AuthRole | null {
  return value === "student" || value === "teacher" ? value : null;
}

/** Sign in / create account. `?mode=signup` and `?role=` preselect the form. */
export default async function Login({ searchParams }: LoginRouteProps) {
  const { mode, role } = await searchParams;
  return <LoginPage startMode={asMode(mode)} defaultRole={asRole(role)} />;
}
