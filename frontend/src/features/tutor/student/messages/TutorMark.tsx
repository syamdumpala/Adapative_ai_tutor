/** The small conic "m" mark shown beside every tutor message. */
export function TutorMark() {
  return (
    <div
      style={{
        background:
          "conic-gradient(from -90deg, var(--color-green), var(--color-green-d))",
      }}
      className="mt-[2px] grid h-[30px] w-[30px] flex-none place-items-center rounded-[9px] font-display text-[14px] font-extrabold text-white"
    >
      m
    </div>
  );
}
