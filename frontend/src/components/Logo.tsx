import { cn } from "@/lib/cn";

interface LogoProps {
  /** Size of the square mark in pixels. Wordmark scales from it. */
  size?: number;
  /** Show the "Adaptive tutor" tagline under the wordmark. */
  showTagline?: boolean;
  /** `solid` = conic-gradient mark on light; `ghost` = translucent for dark panels. */
  variant?: "solid" | "ghost";
  /** Show the wordmark next to the mark. */
  showWordmark?: boolean;
  onClick?: () => void;
  className?: string;
}

const SOLID_MARK =
  "conic-gradient(from -90deg, var(--color-green) 0 50%, var(--color-green-d) 50% 100%)";

function LogoMark({ size, ghost }: { size: number; ghost: boolean }) {
  const skin = ghost
    ? {
        background: "rgba(255,255,255,0.12)",
        border: "1px solid rgba(255,255,255,0.22)",
      }
    : { background: SOLID_MARK };
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: Math.round(size * 0.31),
        fontSize: Math.round(size * 0.47),
        ...skin,
      }}
      className={cn(
        "grid flex-none place-items-center font-display font-extrabold text-white",
        !ghost && "shadow-soft",
      )}
    >
      m
    </div>
  );
}

function Wordmark({
  size,
  ghost,
  showTagline,
}: {
  size: number;
  ghost: boolean;
  showTagline: boolean;
}) {
  return (
    <div className="min-w-0">
      <div
        style={{ fontSize: Math.round(size * 0.47) }}
        className={cn(
          "font-display font-extrabold leading-none tracking-[-0.02em]",
          ghost ? "text-white" : "text-ink",
        )}
      >
        Mira
      </div>
      {showTagline && (
        <div
          className={cn(
            "mt-[3px] font-mono text-[9.5px] uppercase tracking-[0.14em]",
            ghost ? "text-white/60" : "text-ink3",
          )}
        >
          Adaptive tutor
        </div>
      )}
    </div>
  );
}

/** The Mira mark + wordmark, used in the topbar and on the auth screens. */
export function Logo({
  size = 38,
  showTagline = true,
  variant = "solid",
  showWordmark = true,
  onClick,
  className,
}: LogoProps) {
  const ghost = variant === "ghost";
  return (
    <div
      onClick={onClick}
      className={cn(
        "flex min-w-0 items-center gap-[11px]",
        onClick && "cursor-pointer",
        className,
      )}
    >
      <LogoMark size={size} ghost={ghost} />
      {showWordmark && (
        <Wordmark size={size} ghost={ghost} showTagline={showTagline} />
      )}
    </div>
  );
}
