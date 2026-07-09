import { cn } from "@/lib/cn";
import type { AuthRole } from "./types";

interface RolePickerProps {
  role: AuthRole | null;
  onPick: (role: AuthRole) => void;
  error?: string;
}

const ROLES: { value: AuthRole; title: string; desc: string }[] = [
  {
    value: "student",
    title: "Student",
    desc: "Learn with your adaptive tutor",
  },
  {
    value: "teacher",
    title: "Teacher",
    desc: "Track your class & assign reviews",
  },
];

/** Radio-style "Continue as" student/teacher chooser. */
export function RolePicker({ role, onPick, error }: RolePickerProps) {
  return (
    <div>
      <div className="mb-[9px] font-mono text-[10.5px] uppercase tracking-[0.14em] text-ink3">
        Continue as
      </div>
      <div className="grid grid-cols-2 gap-[10px]">
        {ROLES.map((option) => {
          const active = role === option.value;
          return (
            <button
              key={option.value}
              type="button"
              aria-pressed={active}
              onClick={() => onPick(option.value)}
              className={cn(
                "rounded-md border-[1.5px] px-[14px] py-[13px] text-left transition",
                active
                  ? "border-green bg-green-s2 shadow-[0_0_0_3px_var(--color-green-s)]"
                  : cn("bg-card", error ? "border-coral" : "border-line"),
              )}
            >
              <div className="flex items-center gap-[9px]">
                <span
                  className={cn(
                    "h-4 w-4 flex-none rounded-full bg-white transition",
                    active
                      ? "border-[5px] border-green"
                      : "border-[1.5px] border-line",
                  )}
                />
                <span className="text-[14.5px] font-bold">{option.title}</span>
              </div>
              <div className="mt-[6px] text-[11.5px] leading-[1.4] text-ink2">
                {option.desc}
              </div>
            </button>
          );
        })}
      </div>
      {error && (
        <p className="mt-[8px] text-[11.5px] font-semibold text-coral-d">
          {error}
        </p>
      )}
    </div>
  );
}
