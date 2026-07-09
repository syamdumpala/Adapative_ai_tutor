import { TutorMark } from "./TutorMark";

function Dot({ delaySec }: { delaySec: number }) {
  return (
    <span
      style={{ animation: `typing 1.2s ${delaySec}s infinite` }}
      className="h-[7px] w-[7px] rounded-full bg-ink3"
    />
  );
}

/** Three-dot "Mira is typing" bubble. */
export function TypingIndicator() {
  return (
    <div className="flex animate-fade-in items-end gap-[10px]">
      <TutorMark />
      <div className="flex gap-[5px] rounded-[16px_16px_16px_5px] border border-line bg-card px-4 py-[14px] shadow-soft">
        <Dot delaySec={0} />
        <Dot delaySec={0.2} />
        <Dot delaySec={0.4} />
      </div>
    </div>
  );
}
