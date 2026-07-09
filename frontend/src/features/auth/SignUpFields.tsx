import { TextField } from "@/components";
import { cn } from "@/lib/cn";
import { PasswordField } from "./PasswordField";
import { RolePicker } from "./RolePicker";
import type { SignUpInput } from "./types";
import type { UseAuthForm } from "./useAuthForm";
import { passwordRequirements } from "./validation";

function PasswordHints({ value }: { value: string }) {
  return (
    <span className="flex flex-wrap gap-x-3 gap-y-1">
      {passwordRequirements(value).map((req) => (
        <span
          key={req.label}
          className={cn(
            "inline-flex items-center gap-1",
            req.met ? "text-green-d" : "text-ink3",
          )}
        >
          <span aria-hidden>{req.met ? "✓" : "○"}</span>
          {req.label}
        </span>
      ))}
    </span>
  );
}

/** The full stack of sign-up inputs, bound to the form. */
export function SignUpFields({ form }: { form: UseAuthForm<SignUpInput> }) {
  return (
    <>
      <TextField
        {...form.field("name")}
        label="Full name"
        autoComplete="name"
        placeholder="e.g. Maya Chen"
      />
      <TextField
        {...form.field("email")}
        label="Email"
        type="email"
        autoComplete="email"
        placeholder="you@school.edu"
      />
      <PasswordField
        {...form.field("password")}
        label="Password"
        autoComplete="new-password"
        placeholder="Create a password"
        hint={<PasswordHints value={form.values.password} />}
      />
      <PasswordField
        {...form.field("confirm")}
        label="Confirm password"
        autoComplete="new-password"
        placeholder="Re-enter your password"
      />
      <RolePicker
        role={form.values.role}
        onPick={(role) => form.setField("role", role)}
        error={form.errors.role}
      />
    </>
  );
}
