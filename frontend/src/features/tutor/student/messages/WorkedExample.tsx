import { cn } from "@/lib/cn";

interface BarRowProps {
  label: string;
  note: string;
  /** One entry per equal piece; `true` = the shaded (first) piece. */
  filled: boolean;
  pieces: number;
  fillClassName: string;
}

function BarRow({ label, note, filled, pieces, fillClassName }: BarRowProps) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-[12px]">
        <span className="font-bold">{label}</span>
        <span className="text-ink2">{note}</span>
      </div>
      <div className="flex h-[22px] gap-[2px] overflow-hidden rounded-[7px]">
        {Array.from({ length: pieces }, (_, index) => (
          <div
            key={index}
            className={cn(
              "flex-1",
              index === 0 && filled ? fillClassName : "bg-wash",
            )}
          />
        ))}
      </div>
    </div>
  );
}

/** Worked example: the same idea shown on 1/2 versus 1/4. */
export function WorkedExample() {
  return (
    <div className="flex flex-col gap-[11px]">
      <div className="font-mono text-[10px] uppercase tracking-[0.12em] text-green-d">
        Worked example · different numbers
      </div>
      <div className="flex flex-col gap-[9px]">
        <BarRow
          label="1/2"
          note="1 of 2 equal pieces"
          filled
          pieces={2}
          fillClassName="bg-green"
        />
        <BarRow
          label="1/4"
          note="1 of 4 equal pieces"
          filled
          pieces={4}
          fillClassName="bg-coral"
        />
      </div>
      <div className="text-[12.5px] text-ink2">
        Fewer pieces → each piece is <b className="text-ink">bigger</b>. Same
        idea carries to yours.
      </div>
    </div>
  );
}
