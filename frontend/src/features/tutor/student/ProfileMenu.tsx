"use client";

import { useState, type ReactNode } from "react";
import { Avatar } from "@/components";
import { cn } from "@/lib/cn";
import { fullName } from "../data/student";

interface ProfileMenuProps {
  name: string;
  initials: string;
  onProfile: () => void;
  onPerformance: () => void;
  onAnalytics: () => void;
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

function AccountDropdown({
  name,
  initials,
  close,
  onProfile,
  onAnalytics,
  onLogout,
}: ProfileMenuProps & { close: () => void }) {
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
      <div className="absolute right-0 top-[calc(100%+8px)] z-[51] w-[236px] animate-fade-up overflow-hidden rounded-md border border-line bg-card shadow-pop">
        <div className="flex items-center gap-[11px] border-b border-line bg-paper2 px-[15px] py-[14px]">
          <Avatar initials={initials} gradient="violet" size={38} />
          <div className="min-w-0">
            <div className="text-[13.5px] font-bold">{fullName(name)}</div>
          </div>
        </div>
        <div className="p-[6px]">
          <MenuItem icon="◔" onClick={run(onProfile)}>
            Profile
          </MenuItem>
          <MenuItem icon="▩" onClick={run(onAnalytics)}>
            My progress
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

/** Account button that opens the profile / performance / logout dropdown. */
export function ProfileMenu({
  name,
  initials,
  onProfile,
  onPerformance,
  onAnalytics,
  onLogout,
}: ProfileMenuProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative flex-none">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex items-center gap-[11px] rounded-full border border-line bg-card py-[7px] pl-[14px] pr-[11px] shadow-soft transition hover:border-line2"
      >
        <span className="text-right leading-[1.15]">
          <span className="block text-[13px] font-bold">{fullName(name)}</span>
        </span>
        <Avatar initials={initials} gradient="violet" size={34} />
        <span className="text-[10px] text-ink3">▾</span>
      </button>
      {open && (
        <AccountDropdown
          name={name}
          initials={initials}
          close={() => setOpen(false)}
          onProfile={onProfile}
          onPerformance={onPerformance}
          onAnalytics={onAnalytics}
          onLogout={onLogout}
        />
      )}
    </div>
  );
}
