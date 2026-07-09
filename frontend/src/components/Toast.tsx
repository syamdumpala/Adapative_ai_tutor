interface ToastProps {
  /** Message to show, or `null`/empty to render nothing. */
  message: string | null;
}

/** Fixed, top-center transient notification. Pair with `useToast`. */
export function Toast({ message }: ToastProps) {
  if (!message) return null;
  return (
    <div className="fixed left-1/2 top-[72px] z-[80] flex -translate-x-1/2 animate-fade-up items-center gap-[9px] rounded-full bg-ink px-[18px] py-[10px] text-[13px] font-semibold text-paper shadow-pop">
      <span className="text-amber">◷</span>
      {message}
    </div>
  );
}
