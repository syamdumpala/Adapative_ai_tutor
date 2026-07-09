"use client";

import { useRouter } from "next/navigation";
import { useResponsive } from "@/hooks/useResponsive";
import { MIRA_BACKDROP } from "@/lib/backdrop";
import { AuthCard } from "./AuthCard";
import { BrandPanel } from "./BrandPanel";
import type { AuthMode, AuthRole, AuthUser } from "./types";

interface LoginPageProps {
  startMode?: AuthMode;
  defaultRole?: AuthRole | null;
}

/** Full-screen auth layout: brand panel (wide screens) beside the auth card. */
export function LoginPage({
  startMode = "signin",
  defaultRole = null,
}: LoginPageProps) {
  const bp = useResponsive();
  const router = useRouter();
  // Once the API is wired, `user.role` comes from the server; routing into the
  // tutor by role is the integration point.
  const onAuthed = (user: AuthUser) =>
    router.push(user.role === "teacher" ? "/?role=teacher" : "/");

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ background: MIRA_BACKDROP }}
    >
      {bp !== "mobile" && <BrandPanel />}
      <main className="grid min-w-0 flex-1 place-items-center overflow-auto p-[clamp(18px,4vw,48px)]">
        <AuthCard
          startMode={startMode}
          defaultRole={defaultRole}
          onAuthed={onAuthed}
        />
      </main>
    </div>
  );
}
