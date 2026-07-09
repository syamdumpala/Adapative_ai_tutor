import { Logo } from "@/components";

interface TopbarProps {
  onLogoClick: () => void;
}

/** Sticky app header: brand only. Role is fixed by the signed-in account. */
export function Topbar({ onLogoClick }: TopbarProps) {
  return (
    <header className="sticky top-0 z-40 flex items-center gap-[18px] border-b border-line bg-[rgba(250,246,238,0.82)] px-[clamp(14px,3vw,30px)] py-3 backdrop-blur-[14px]">
      <Logo onClick={onLogoClick} />
    </header>
  );
}
