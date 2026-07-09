/** A small "?" circle that reveals an explanatory paragraph on hover or focus. */
export function InfoDot({
  text,
  label = "About this chart",
}: {
  text: string;
  label?: string;
}) {
  return (
    <span className="group relative inline-flex flex-none">
      <button
        type="button"
        aria-label={label}
        className="grid h-[18px] w-[18px] place-items-center rounded-full border border-line bg-paper2 text-[11px] font-bold text-ink3 transition hover:border-line2 hover:text-ink2 focus:outline-none focus-visible:border-violet focus-visible:text-ink2"
      >
        ?
      </button>
      <span
        role="tooltip"
        className="pointer-events-none absolute right-0 top-[calc(100%+8px)] z-[60] w-[264px] rounded-md border border-line bg-card p-[12px] text-[12px] leading-[1.55] text-ink2 opacity-0 shadow-pop transition-opacity duration-150 group-hover:opacity-100 group-focus-within:opacity-100"
      >
        {text}
      </span>
    </span>
  );
}
