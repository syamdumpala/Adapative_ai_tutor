import type { HTMLInputTypeAttribute, KeyboardEvent, ReactNode } from "react";
import { cn } from "@/lib/cn";

interface TextFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  id?: string;
  type?: HTMLInputTypeAttribute;
  placeholder?: string;
  autoComplete?: string;
  disabled?: boolean;
  onKeyDown?: (event: KeyboardEvent<HTMLInputElement>) => void;
  onBlur?: () => void;
  /** Inline validation message; also switches the field to the error style. */
  error?: string;
  /** Muted helper text shown when there is no error. */
  hint?: ReactNode;
  /** Element rendered on the right of the label row (e.g. a link). */
  labelAction?: ReactNode;
  /** Element floated inside the field's right edge (e.g. a toggle). */
  trailing?: ReactNode;
  /** Reserve room on the right for a wider `trailing` control. */
  reserveTrailing?: boolean;
}

const OK_FOCUS =
  "border-line focus:border-green focus:shadow-[0_0_0_3px_var(--color-green-s)]";
const ERR_FOCUS =
  "border-coral focus:border-coral focus:shadow-[0_0_0_3px_var(--color-coral-s)]";

function FieldMessage({
  id,
  error,
  hint,
}: {
  id?: string;
  error?: string;
  hint?: ReactNode;
}) {
  if (error) {
    return (
      <p id={id} className="mt-[6px] text-[11.5px] font-semibold text-coral-d">
        {error}
      </p>
    );
  }
  if (hint)
    return <div className="mt-[6px] text-[11.5px] text-ink3">{hint}</div>;
  return null;
}

/** Labeled form input with inline errors, the Mira focus ring, and ARIA wiring. */
export function TextField(props: TextFieldProps) {
  const {
    label,
    value,
    onChange,
    id,
    type = "text",
    error,
    hint,
    labelAction,
    trailing,
  } = props;
  const describedBy = error && id ? `${id}-error` : undefined;
  return (
    <div>
      <div className="mb-[6px] flex items-baseline justify-between">
        <label htmlFor={id} className="text-[12.5px] font-semibold text-ink2">
          {label}
        </label>
        {labelAction}
      </div>
      <div className="relative">
        <input
          id={id}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={props.onKeyDown}
          onBlur={props.onBlur}
          type={type}
          placeholder={props.placeholder}
          autoComplete={props.autoComplete}
          disabled={props.disabled}
          aria-invalid={Boolean(error)}
          aria-describedby={describedBy}
          className={cn(
            "h-[46px] w-full rounded-[12px] border-[1.5px] bg-paper px-[14px] text-[14px] text-ink outline-none transition disabled:opacity-60",
            props.reserveTrailing && "pr-[66px]",
            error ? ERR_FOCUS : OK_FOCUS,
          )}
        />
        {trailing}
      </div>
      <FieldMessage id={describedBy} error={error} hint={hint} />
    </div>
  );
}
