import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

type ButtonVariant = "primary" | "secondary" | "success";
type ButtonSize = "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
}

const variantClass: Record<ButtonVariant, string> = {
  primary: "bg-ink text-paper font-bold shadow-soft hover:-translate-y-px",
  secondary:
    "border border-line bg-card text-ink2 font-semibold hover:bg-paper2",
  success: "bg-green text-white font-bold shadow-float hover:bg-green-d",
};

const sizeClass: Record<ButtonSize, string> = {
  md: "h-10 rounded-[11px] px-[18px] text-[13.5px]",
  lg: "h-12 rounded-[13px] px-5 text-[14.5px]",
};

/** The primary action element across Mira: dialogue replies, banners, forms. */
export function Button({
  variant = "primary",
  size = "md",
  fullWidth = false,
  className,
  type = "button",
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-[9px] transition",
        variantClass[variant],
        sizeClass[size],
        fullWidth && "w-full",
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  );
}
