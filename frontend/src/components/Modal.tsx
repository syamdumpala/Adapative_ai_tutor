"use client";

import { useEffect, type ReactNode } from "react";
import { IconButton } from "./IconButton";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  /** Maximum panel width in pixels. */
  width?: number;
}

/** Centered overlay dialog: click-outside and Escape both close it. */
export function Modal({
  open,
  onClose,
  title,
  children,
  width = 440,
}: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      role="presentation"
      onClick={onClose}
      className="fixed inset-0 z-[90] grid animate-fade-in place-items-center bg-[rgba(35,32,25,0.45)] p-5"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
        style={{ width: `min(${width}px, 100%)` }}
        className="animate-pop overflow-hidden rounded-xl border border-line bg-card shadow-pop"
      >
        <div className="flex items-center justify-between gap-[10px] border-b border-line px-[18px] py-4">
          <div className="font-display text-[17px] font-bold">{title}</div>
          <IconButton
            variant="paper"
            size={32}
            radius="rounded-[9px]"
            onClick={onClose}
            aria-label="Close"
          >
            ✕
          </IconButton>
        </div>
        {children}
      </div>
    </div>
  );
}
