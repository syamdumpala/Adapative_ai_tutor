"use client";

import { useState } from "react";
import { Card, Logo, SegmentedControl } from "@/components";
import { SignInForm } from "./SignInForm";
import { SignUpForm } from "./SignUpForm";
import type { AuthMode, AuthRole, AuthUser } from "./types";

interface AuthCardProps {
  startMode: AuthMode;
  defaultRole: AuthRole | null;
  onAuthed: (user: AuthUser) => void;
}

const MODE_OPTIONS: { value: AuthMode; label: string }[] = [
  { value: "signin", label: "Sign in" },
  { value: "signup", label: "Create account" },
];

/** The auth card: brand, mode toggle, the active form, and the mode switch. */
export function AuthCard({ startMode, defaultRole, onAuthed }: AuthCardProps) {
  const [mode, setMode] = useState<AuthMode>(startMode);
  const isSignup = mode === "signup";

  return (
    <Card className="w-[min(440px,100%)] animate-fade-up rounded-xl p-[clamp(24px,3.4vw,34px)] shadow-pop">
      <div className="mb-5">
        <Logo size={34} showTagline={false} />
      </div>
      <h1 className="text-[26px] font-extrabold">
        {isSignup ? "Create your account" : "Welcome back"}
      </h1>
      <p className="mt-[6px] text-[13.5px] text-ink2">
        {isSignup
          ? "Join Mira — pick your role to get started."
          : "Sign in to pick up where you left off."}
      </p>
      <SegmentedControl
        variant="card"
        stretch
        className="mt-5"
        options={MODE_OPTIONS}
        value={mode}
        onChange={setMode}
      />
      <div className="mt-[18px]">
        {isSignup ? (
          <SignUpForm onAuthed={onAuthed} defaultRole={defaultRole} />
        ) : (
          <SignInForm onAuthed={onAuthed} />
        )}
      </div>
      <div className="mt-[18px] text-center text-[13px] text-ink2">
        {isSignup ? "Already have an account?" : "New to Mira?"}{" "}
        <button
          type="button"
          onClick={() => setMode(isSignup ? "signin" : "signup")}
          className="font-bold text-green transition hover:text-green-d"
        >
          {isSignup ? "Sign in" : "Create one"}
        </button>
      </div>
    </Card>
  );
}
