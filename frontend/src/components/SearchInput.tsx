import { cn } from "@/lib/cn";
import { SearchIcon } from "./icons";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  /** Input height in pixels. */
  height?: number;
  className?: string;
}

const FIELD_FOCUS =
  "focus:border-green focus:shadow-[0_0_0_3px_var(--color-green-s)]";

/** Text input with a leading search glyph and the Mira focus ring. */
export function SearchInput({
  value,
  onChange,
  placeholder,
  height = 40,
  className,
}: SearchInputProps) {
  return (
    <div className={cn("relative", className)}>
      <span className="pointer-events-none absolute left-[13px] top-1/2 grid -translate-y-1/2 place-items-center text-ink3">
        <SearchIcon />
      </span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        style={{ height }}
        className={cn(
          "w-full rounded-[11px] border border-line bg-card pl-[38px] pr-[14px] text-[13.5px] text-ink outline-none transition",
          FIELD_FOCUS,
        )}
      />
    </div>
  );
}
