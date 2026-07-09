"use client";

import { useState } from "react";
import { IconButton } from "@/components";
import { cn } from "@/lib/cn";

interface ComposerProps {
  hintRung: number;
  onSend: (text: string) => void;
}

function HintBadge({ rung }: { rung: number }) {
  return (
    <div className="mb-[11px] flex flex-wrap items-center gap-[9px]">
      <span className="inline-flex items-center gap-[8px] rounded-full bg-coral-s px-[11px] py-1 text-[12.5px] font-bold text-coral-d">
        Hint {rung} of 3
        <span className="flex gap-[3px]">
          {[1, 2, 3].map((dot) => (
            <span
              key={dot}
              className={cn(
                "h-[6px] w-[6px] rounded-full",
                dot <= rung ? "bg-coral-d" : "bg-[rgba(194,71,38,0.28)]",
              )}
            />
          ))}
        </span>
      </span>
    </div>
  );
}

/** Hint status + the free-text message field wired to the live tutor. */
export function Composer({ hintRung, onSend }: ComposerProps) {
  const [draft, setDraft] = useState("");
  const submit = () => {
    if (!draft.trim()) return;
    onSend(draft);
    setDraft("");
  };

  return (
    <>
      {hintRung > 0 && <HintBadge rung={hintRung} />}
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
    </>
  );
}
