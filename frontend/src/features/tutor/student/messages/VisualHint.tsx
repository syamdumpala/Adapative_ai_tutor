const RING = "absolute inset-0 rounded-full border-2 border-white/70";

/** The two-pizza visual hint: halves versus thirds. */
export function VisualHint() {
  return (
    <div className="flex flex-wrap justify-center gap-[18px] py-1">
      <div className="text-center">
        <div
          style={{
            background:
              "conic-gradient(var(--color-green) 0 180deg, var(--color-green-s) 180deg 360deg)",
            animation: "spinIn 0.5s both",
          }}
          className="relative h-[96px] w-[96px] rounded-full shadow-soft"
        >
          <div className={RING} />
          <div className="absolute left-1/2 top-0 h-full w-[2px] -translate-x-1/2 bg-white/80" />
        </div>
        <div className="mt-2 text-[13px] font-bold">cut into 2</div>
        <div className="text-[11.5px] text-ink2">
          each piece = <b className="text-green-d">1/2</b>
        </div>
      </div>
      <div className="text-center">
        <div
          style={{
            background:
              "conic-gradient(var(--color-coral) 0 120deg, var(--color-coral-s) 120deg 360deg)",
            animation: "spinIn 0.5s 0.08s both",
          }}
          className="relative h-[96px] w-[96px] rounded-full shadow-soft"
        >
          <div className={RING} />
          {[-90, 30, 150].map((deg) => (
            <div
              key={deg}
              style={{
                transformOrigin: "left center",
                transform: `rotate(${deg}deg)`,
              }}
              className="absolute left-1/2 top-1/2 h-[2px] w-[48px] bg-white/80"
            />
          ))}
        </div>
        <div className="mt-2 text-[13px] font-bold">cut into 3</div>
        <div className="text-[11.5px] text-ink2">
          each piece = <b className="text-coral-d">1/3</b>
        </div>
      </div>
    </div>
  );
}
