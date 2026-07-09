import { Logo } from "@/components";

const FEATURES = [
  {
    title: "Adaptive diagnosis",
    desc: "Finds the why behind every mistake, not just the wrong answer.",
  },
  {
    title: "Spaced review",
    desc: "Resurfaces skills right before they fade from memory.",
  },
  {
    title: "Teacher insights",
    desc: "Class-wide misconception radar and one-tap review assignments.",
  },
];

const PANEL_BG =
  "linear-gradient(168deg, #10744F 0%, var(--color-green-d) 55%, #083D2C 100%)";

function Feature({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="flex items-start gap-3">
      <span className="mt-[1px] grid h-[22px] w-[22px] flex-none place-items-center rounded-full border border-white/20 bg-white/[0.14] text-[11px]">
        ✓
      </span>
      <div>
        <div className="text-[14.5px] font-bold">{title}</div>
        <div className="mt-[2px] text-[12.5px] text-white/[0.68]">{desc}</div>
      </div>
    </div>
  );
}

/** Marketing panel shown beside the auth card on wide screens. */
export function BrandPanel() {
  return (
    <aside
      style={{ background: PANEL_BG }}
      className="relative flex w-[clamp(380px,40vw,560px)] flex-none flex-col justify-between gap-10 overflow-hidden p-[clamp(30px,4vw,54px)] text-white"
    >
      <div
        aria-hidden
        style={{
          background:
            "radial-gradient(closest-side, rgba(255,255,255,0.09), transparent 70%)",
        }}
        className="pointer-events-none absolute -right-[180px] -top-[200px] h-[520px] w-[520px] rounded-full"
      />
      <div
        aria-hidden
        style={{
          background:
            "radial-gradient(closest-side, rgba(18,128,92,0.5), transparent 72%)",
        }}
        className="pointer-events-none absolute -bottom-[190px] -left-[160px] h-[460px] w-[460px] rounded-full"
      />
      <Logo variant="ghost" size={40} className="relative" />
      <div className="relative flex max-w-[420px] flex-col gap-[26px]">
        <h1 className="text-[clamp(28px,2.9vw,40px)] font-extrabold tracking-[-0.02em] text-white">
          Tutoring that adapts to every student.
        </h1>
        <div className="flex flex-col gap-[15px]">
          {FEATURES.map((feature) => (
            <Feature
              key={feature.title}
              title={feature.title}
              desc={feature.desc}
            />
          ))}
        </div>
      </div>
      <div className="relative font-mono text-[10px] uppercase tracking-[0.16em] text-white/50">
        Mira · Adaptive tutoring platform
      </div>
    </aside>
  );
}
