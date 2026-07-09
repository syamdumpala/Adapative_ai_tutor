import { redirect } from "next/navigation";
import { TutorApp } from "@/features/tutor/TutorApp";
import { backendFetch, readToken } from "@/server/backend";

/**
 * Mira Tutor entry point. Requires a valid session: the role and display name
 * come from the signed-in account (`/auth/me`), not a query-string shim.
 */
export default async function Home() {
  const token = await readToken();
  const me = token ? await backendFetch("/auth/me", {}, token) : null;
  if (!me || !me.ok) {
    redirect("/login");
  }
  const user = me.body as { first_name?: string; role?: string };
  return (
    <TutorApp
      studentName={user.first_name || "there"}
      initialRole={user.role === "teacher" ? "teacher" : "student"}
    />
  );
}
