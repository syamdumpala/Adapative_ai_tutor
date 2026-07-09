"use client";

import { useEffect, useState } from "react";

export type Breakpoint = "mobile" | "tablet" | "desktop";

function breakpointFor(width: number): Breakpoint {
  if (width < 760) return "mobile";
  if (width < 1180) return "tablet";
  return "desktop";
}

/**
 * Tracks the viewport breakpoint used across the Mira layouts.
 *
 * Starts at `desktop` so server and first client render agree (avoiding a
 * hydration mismatch), then corrects to the real width after mount.
 */
export function useResponsive(): Breakpoint {
  const [bp, setBp] = useState<Breakpoint>("desktop");

  useEffect(() => {
    const update = () => setBp(breakpointFor(window.innerWidth));
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  return bp;
}
