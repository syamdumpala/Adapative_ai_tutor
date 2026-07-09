"use client";

import { type ReactNode, useEffect, useState } from "react";
import { Avatar } from "@/components";
import { cn } from "@/lib/cn";

interface TeacherAccountMenuProps {
  name: string;
  initials: string;
  onProfile: () => void;
  onLogout: () => void;
}

function MenuItem({
  icon,
  danger = false,
  onClick,
  children,
}: {
  icon: string;
  danger?: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      role="menuitem"
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-[11px] rounded-[9px] bg-transparent px-[11px] py-[10px] text-left text-[13px] font-semibold transition",
        danger ? "text-coral-d hover:bg-coral-s" : "text-ink hover:bg-paper2",
      )}
    >
      <span
        className={cn(
          "w-[18px] text-center text-[14px]",
          !danger && "text-ink3",
        )}
      >
        {icon}
      </span>
      {children}
    </button>
  );
}

function Dropdown({
  name,
  initials,
  close,
  onProfile,
  onLogout,
}: TeacherAccountMenuProps & { close: () => void }) {
  const run = (action: () => void) => () => {
    close();
    action();
  };
  return (
    <>
      <div
        role="presentation"
        onClick={close}
        className="fixed inset-0 z-[50]"
      />
      <div
        role="menu"
        className="absolute right-0 top-[calc(100%+8px)] z-[51] w-[220px] animate-fade-up overflow-hidden rounded-md border border-line bg-card shadow-pop"
      >
        <div className="flex items-center gap-[11px] border-b border-line bg-paper2 px-[15px] py-[14px]">
          <Avatar initials={initials} gradient="violet" size={38} />
          <div className="min-w-0">
            <div className="truncate text-[13.5px] font-bold">{name}</div>
            <div className="text-[11px] text-ink2">Teacher</div>
          </div>
        </div>
        <div className="p-[6px]">
          <MenuItem icon="◔" onClick={run(onProfile)}>
            Profile
          </MenuItem>
        </div>
        <div className="border-t border-line p-[6px]">
          <MenuItem icon="⏻" danger onClick={run(onLogout)}>
            Log out
          </MenuItem>
        </div>
      </div>
    </>
  );
}

/** Teacher profile avatar that opens a profile / logout dropdown. */
export function TeacherAccountMenu({
  name,
  initials,
  onProfile,
  onLogout,
}: TeacherAccountMenuProps) {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);
  return (
    <div className="relative flex-none">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        title="Account"
        aria-haspopup="menu"
        aria-expanded={open}
        className="flex items-center gap-[7px] rounded-full border border-line bg-card py-[6px] pl-[7px] pr-[10px] shadow-soft transition hover:border-line2"
      >
        <Avatar initials={initials} gradient="violet" size={32} />
        <span className="text-[10px] text-ink3">▾</span>
      </button>
      {open && (
        <Dropdown
          name={name}
          initials={initials}
          close={() => setOpen(false)}
          onProfile={onProfile}
          onLogout={onLogout}
        />
      )}
    </div>
  );
}
