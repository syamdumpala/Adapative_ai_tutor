"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const TOAST_DURATION_MS = 2600;

export interface ToastController {
  /** The current toast message, or `null` when nothing is showing. */
  message: string | null;
  /** Show a message; it auto-dismisses after a short delay. */
  show: (message: string) => void;
}

/** Transient, auto-dismissing toast notifications. */
export function useToast(): ToastController {
  const [message, setMessage] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const show = useCallback((next: string) => {
    setMessage(next);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setMessage(null), TOAST_DURATION_MS);
  }, []);

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current);
    },
    [],
  );

  return { message, show };
}
