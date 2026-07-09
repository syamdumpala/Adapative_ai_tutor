import { cn } from "@/lib/cn";
import { avatarGradient, type GradientTone } from "@/lib/tones";

interface AvatarProps {
  initials: string;
  gradient: GradientTone;
  /** Square edge length in pixels. */
  size?: number;
  /** Use the display face at heavier weight (hero avatars). */
  display?: boolean;
  className?: string;
}

/** Gradient-filled square holding a person's initials. */
export function Avatar({
  initials,
  gradient,
  size = 42,
  display = false,
  className,
}: AvatarProps) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: Math.round(size * 0.28),
        fontSize: Math.round(size * (display ? 0.4 : 0.37)),
        background: avatarGradient[gradient],
      }}
      className={cn(
        "grid flex-none place-items-center text-white",
        display ? "font-display font-extrabold" : "font-bold",
        className,
      )}
    >
      {initials}
    </div>
  );
}
