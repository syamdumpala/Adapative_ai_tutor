import { cn } from "@/lib/cn";
import type { TeacherScreen } from "../types";
import { TeacherAccountMenu } from "./TeacherAccountMenu";

interface TeacherToolbarProps {
  screen: TeacherScreen;
  canGoBack: boolean;
  onBack: () => void;
  onCatalog: () => void;
  onProfile: () => void;
  onLogout: () => void;
  name: string;
  initials: string;
}

const CRUMB: Record<TeacherScreen, string> = {
  home: "Teacher · Home",
  topic: "Teacher · Topic",
  student: "Teacher · Student",
  catalog: "Teacher · Catalog",
};

/** Teacher toolbar: back control + breadcrumb, add-topic, and account menu. */
export function TeacherToolbar({
  screen,
  canGoBack,
  onBack,
  onCatalog,
  onProfile,
  onLogout,
  name,
  initials,
}: TeacherToolbarProps) {
  return (
    <div className="flex items-center justify-between gap-3">
      <button
        type="button"
        onClick={onBack}
        disabled={!canGoBack}
        title={canGoBack ? "Back" : undefined}
        className={cn(
          "flex items-center gap-[7px] font-mono text-[10px] uppercase tracking-[0.14em] transition",
          canGoBack ? "text-ink2 hover:text-ink" : "cursor-default text-ink3",
        )}
      >
        <span
          className={cn("text-[15px] leading-none", !canGoBack && "opacity-30")}
        >
          ‹
        </span>
        {CRUMB[screen]}
      </button>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onCatalog}
          title="Add & manage topics"
          className="inline-flex h-[38px] items-center gap-[6px] rounded-full border border-line bg-card px-[15px] text-[13px] font-semibold text-ink2 shadow-soft transition hover:bg-paper2"
        >
          <span className="text-[15px] leading-none">＋</span>Topic
        </button>
        <TeacherAccountMenu
          name={name}
          initials={initials}
          onProfile={onProfile}
          onLogout={onLogout}
        />
      </div>
    </div>
  );
}
