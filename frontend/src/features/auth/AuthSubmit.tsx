import { Button } from "@/components";

interface AuthSubmitProps {
  submitting: boolean;
  /** Label at rest. */
  idle: string;
  /** Label while submitting. */
  busy: string;
}

/** Full-width form submit button with a spinner while pending. */
export function AuthSubmit({ submitting, idle, busy }: AuthSubmitProps) {
  return (
    <Button
      type="submit"
      variant="success"
      size="lg"
      fullWidth
      disabled={submitting}
      className={submitting ? "pointer-events-none opacity-75" : ""}
    >
      {submitting && (
        <span
          style={{ animation: "spin 0.7s linear infinite" }}
          className="h-[15px] w-[15px] rounded-full border-2 border-white/40 border-t-white"
        />
      )}
      {submitting ? busy : idle}
    </Button>
  );
}
