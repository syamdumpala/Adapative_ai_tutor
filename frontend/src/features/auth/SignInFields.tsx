import { Checkbox, TextField } from "@/components";
import { requestPasswordReset } from "./api";
import { PasswordField } from "./PasswordField";
import type { SignInInput } from "./types";
import type { UseAuthForm } from "./useAuthForm";
import { validateEmail } from "./validation";

async function sendReset(form: UseAuthForm<SignInInput>): Promise<void> {
  const emailError = validateEmail(form.values.email);
  if (emailError) {
    form.setFieldError("email", emailError);
    return;
  }
  const email = form.values.email.trim();
  try {
    await requestPasswordReset(email);
    form.setNotice(
      `If an account exists for ${email}, a reset link is on the way.`,
    );
  } catch {
    form.setNotice("Password reset opens up once the auth API is connected.");
  }
}

/** Email + password + remember-me + a "forgot password" reset request. */
export function SignInFields({ form }: { form: UseAuthForm<SignInInput> }) {
  const forgotLink = (
    <button
      type="button"
      onClick={() => void sendReset(form)}
      className="text-[12px] font-semibold text-green transition hover:text-green-d"
    >
      Forgot password?
    </button>
  );
  return (
    <>
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
        autoComplete="current-password"
        placeholder="Your password"
        labelAction={forgotLink}
      />
      <Checkbox
        id="remember"
        checked={form.values.remember}
        onChange={(checked) => form.setField("remember", checked)}
        label="Keep me signed in"
      />
    </>
  );
}
