import { Logo, SegmentedControl } from "@/components";
import type { Role } from "./types";

interface TopbarProps {
  role: Role;
  onRole: (role: Role) => void;
  onLogoClick: () => void;
  isTeacher: boolean;
  onSimulateDay: () => void;
  onRestart: () => void;
  /** Show text labels beside the action-button icons (hidden on mobile). */
  showLabels: boolean;
}

const ROLE_OPTIONS: { value: Role; label: string }[] = [
  { value: "student", label: "Student" },
  { value: "teacher", label: "Teacher" },
];

const ACTION_BASE =
  "inline-flex h-[38px] items-center gap-[7px] rounded-full px-[14px] text-[13px] font-semibold shadow-soft transition";

/** Sticky app header: brand, role toggle, and demo controls. */
export function Topbar({
  role,
  onRole,
  onLogoClick,
  isTeacher,
  onSimulateDay,
  onRestart,
  showLabels,
}: TopbarProps) {
  return (
    <header className="sticky top-0 z-40 flex items-center gap-[18px] border-b border-line bg-[rgba(250,246,238,0.82)] px-[clamp(14px,3vw,30px)] py-3 backdrop-blur-[14px]">
      <Logo onClick={onLogoClick} />
      <div className="flex flex-1 justify-center">
        <SegmentedControl
          options={ROLE_OPTIONS}
          value={role}
          onChange={onRole}
        />
      </div>
      <div className="flex items-center gap-2">
        {isTeacher && (
          <button
            type="button"
            onClick={onSimulateDay}
            title="Advance the spaced-repetition clock"
            className={`${ACTION_BASE} border border-line bg-card text-ink2`}
          >
            <span className="text-[14px]">◷</span>
            {showLabels && <span>Simulate day</span>}
          </button>
        )}
        <button
          type="button"
          onClick={onRestart}
          title="Restart the demo"
          className={`${ACTION_BASE} bg-ink text-paper`}
        >
          <span className="text-[13px]">↺</span>
          {showLabels && <span>Restart</span>}
        </button>
      </div>
    </header>
  );
}
