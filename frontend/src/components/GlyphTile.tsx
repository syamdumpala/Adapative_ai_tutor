import { cn } from "@/lib/cn";
import { glyphTileTone, type Tone } from "@/lib/tones";

interface GlyphTileProps {
  /** Short glyph or abbreviation (e.g. "½", "%", "a:b"). */
  glyph: string;
  /** Preset accent tone (defaults to green). */
  tone?: Tone;
  /** Explicit `bg-* text-*` classes, overriding `tone` for off-palette tiles. */
  toneClassName?: string;
  /** Square edge length in pixels. */
  size?: number;
  className?: string;
}

/** Rounded, tinted tile stamped with a subject/topic glyph. */
export function GlyphTile({
  glyph,
  tone = "green",
  toneClassName,
  size = 46,
  className,
}: GlyphTileProps) {
  const big = glyph.length <= 2;
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: Math.round(size * 0.28),
        fontSize: Math.round(size * (big ? 0.46 : 0.32)),
      }}
      className={cn(
        "grid flex-none place-items-center font-display font-extrabold",
        toneClassName ?? glyphTileTone[tone],
        className,
      )}
    >
      {glyph}
    </div>
  );
}
