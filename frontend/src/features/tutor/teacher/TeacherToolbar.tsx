import { HomeIcon, IconButton } from "@/components";
import type { TeacherScreen } from "../types";

interface TeacherToolbarProps {
  screen: TeacherScreen;
  onHome: () => void;
  onLogout: () => void;
}

const CRUMB: Record<TeacherScreen, string> = {
  home: "Teacher · Home",
  topic: "Teacher · Topic",
  student: "Teacher · Student",
};

/** Persistent teacher toolbar: breadcrumb, home button and logout. */
export function TeacherToolbar({
  screen,
  onHome,
  onLogout,
}: TeacherToolbarProps) {
  const atHome = screen === "home";
  return (
    <div className="flex items-center justify-between gap-3">
      <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink3">
        {CRUMB[screen]}
      </div>
      <div className="flex items-center gap-2">
        <IconButton
          variant={atHome ? "ink" : "card"}
          radius="rounded-[11px]"
          onClick={onHome}
          title="Home"
        >
          <HomeIcon />
        </IconButton>
        <button
          type="button"
          onClick={onLogout}
          title="Log out"
          className="inline-flex h-[38px] items-center gap-2 rounded-full border border-line bg-card px-[15px] text-[13px] font-semibold text-coral-d shadow-soft transition hover:bg-coral-s"
        >
          <span className="text-[14px]">⏻</span>Log out
        </button>
      </div>
    </div>
  );
}
