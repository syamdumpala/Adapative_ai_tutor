"use client";

import { useState } from "react";
import { IconButton } from "@/components";

interface ComposerProps {
  onSend: (text: string) => void;
}

/** Free-text message field wired to the live tutor. */
export function Composer({ onSend }: ComposerProps) {
  const [draft, setDraft] = useState("");
  const submit = () => {
    if (!draft.trim()) return;
    onSend(draft);
    setDraft("");
  };

  return (
    <div className="flex items-center gap-[10px] rounded-[14px] border border-line bg-card py-[7px] pl-4 pr-[7px] shadow-soft">
      <input
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={(event) => event.key === "Enter" && submit()}
        placeholder="Type your message to Mira…"
        className="flex-1 border-0 bg-transparent py-[7px] text-[14px] text-ink outline-none"
      />
      <IconButton
        variant="accent"
        onClick={submit}
        title="Send"
        className="text-[16px]"
      >
        ↑
      </IconButton>
    </div>
  );
}
