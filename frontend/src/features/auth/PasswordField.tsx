"use client";

import { useState, type ReactNode } from "react";
import { TextField } from "@/components";

interface PasswordFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete: string;
  error?: string;
  disabled?: boolean;
  placeholder?: string;
  hint?: ReactNode;
  labelAction?: ReactNode;
}

/** Password `TextField` with an inline show / hide toggle. */
export function PasswordField(props: PasswordFieldProps) {
  const [show, setShow] = useState(false);
  const toggle = (
    <button
      type="button"
      onClick={() => setShow((value) => !value)}
      aria-label={show ? "Hide password" : "Show password"}
      className="absolute right-[7px] top-1/2 -translate-y-1/2 rounded-[8px] border border-line bg-paper2 px-[10px] py-[6px] text-[11.5px] font-bold text-ink2 transition hover:text-ink"
    >
      {show ? "Hide" : "Show"}
    </button>
  );
  return (
    <TextField
      id={props.id}
      label={props.label}
      value={props.value}
      onChange={props.onChange}
      error={props.error}
      disabled={props.disabled}
      type={show ? "text" : "password"}
      autoComplete={props.autoComplete}
      placeholder={props.placeholder}
      hint={props.hint}
      labelAction={props.labelAction}
      trailing={toggle}
      reserveTrailing
    />
  );
}
