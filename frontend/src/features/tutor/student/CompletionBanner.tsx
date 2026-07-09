import { Button } from "@/components";

interface CompletionBannerProps {
  onNewChat: () => void;
  onToTeacher: () => void;
}

/** Replaces the composer once a guided conversation is completed. */
export function CompletionBanner({
  onNewChat,
  onToTeacher,
}: CompletionBannerProps) {
  return (
    <div className="flex animate-pop flex-col gap-[13px] rounded-lg border border-green-s bg-green-s2 px-4 py-[15px]">
      <div className="flex items-center gap-[11px]">
        <span className="grid h-8 w-8 flex-none place-items-center rounded-[10px] bg-green text-[16px] text-white">
          ✓
        </span>
        <div className="min-w-0 flex-1">
          <div className="font-display text-[15px] font-bold text-green-d">
            Chat complete — nicely done
          </div>
          <div className="text-[12px] text-ink2">
            This conversation is paused. Start a new chat to ask something else.
          </div>
        </div>
      </div>
      <div className="flex flex-wrap gap-[9px]">
        <Button variant="primary" onClick={onNewChat}>
          Start a new chat
        </Button>
        <Button variant="secondary" onClick={onToTeacher}>
          See teacher view
        </Button>
      </div>
    </div>
  );
}
