"use client";

import { useState } from "react";
import { Button, IconButton } from "@/components";
import { cn } from "@/lib/cn";
import type { Control } from "../types";

interface ComposerProps {
  controls: Control[];
  hintRung: number;
  leakChecks: number;
  onControl: (key: string) => void;
  onSend: (text: string) => void;
}

function HintBadge({ rung, leakChecks }: { rung: number; leakChecks: number }) {
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
      <span className="inline-flex items-center gap-[6px] rounded-full bg-green-s2 px-[10px] py-1 font-mono text-[11px] text-green-d">
        <span className="h-[7px] w-[7px] rounded-full bg-green" />0 leaks ·{" "}
        {leakChecks} checks
      </span>
    </div>
  );
}

/** Hint status, suggested replies, and the free-text message field. */
export function Composer({
  controls,
  hintRung,
  leakChecks,
  onControl,
  onSend,
}: ComposerProps) {
  const [draft, setDraft] = useState("");
  const submit = () => {
    if (!draft.trim()) return;
    onSend(draft);
    setDraft("");
  };

  return (
    <>
      {hintRung > 0 && <HintBadge rung={hintRung} leakChecks={leakChecks} />}
      {controls.length > 0 && (
        <div className="mb-[11px] flex flex-wrap gap-[9px]">
          {controls.map((control) => (
            <Button
              key={control.key}
              variant={control.variant === "primary" ? "primary" : "secondary"}
              onClick={() => onControl(control.key)}
            >
              {control.label}
            </Button>
          ))}
        </div>
      )}
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
