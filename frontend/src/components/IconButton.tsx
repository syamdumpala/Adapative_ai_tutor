import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

type IconButtonVariant = "card" | "paper" | "ink" | "accent";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: IconButtonVariant;
  /** Square edge length in pixels. */
  size?: number;
  /** Tailwind radius utility (defaults to a 10px corner). */
  radius?: string;
}

const variantClass: Record<IconButtonVariant, string> = {
  card: "border border-line bg-card text-ink2 hover:bg-paper2",
  paper: "border border-line bg-paper2 text-ink2 hover:text-coral-d",
  ink: "border border-ink bg-ink text-paper",
  accent: "bg-green text-white shadow-soft hover:brightness-[1.06]",
};

/** Compact square button holding a single glyph or icon (back, close, send…). */
export function IconButton({
  variant = "card",
  size = 38,
  radius = "rounded-[10px]",
  className,
  type = "button",
  children,
  ...rest
}: IconButtonProps) {
  return (
    <button
      type={type}
      style={{ width: size, height: size }}
      className={cn(
        "grid flex-none place-items-center transition",
        radius,
        variantClass[variant],
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  );
}
