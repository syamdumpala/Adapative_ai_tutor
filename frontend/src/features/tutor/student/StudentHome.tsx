import type { ReactNode } from "react";
import type { Breakpoint } from "@/hooks/useResponsive";
import type { MiraChat } from "../hooks/useMiraChat";
import { ChatsSidebar } from "./ChatsSidebar";
import { TopicGrid } from "./TopicGrid";

interface StudentHomeProps {
  chat: MiraChat;
  name: string;
  initials: string;
  bp: Breakpoint;
  onProfile: () => void;
  onPerformance: () => void;
  onLogout: () => void;
}

function MobileHome({
  grid,
  sidebar,
}: {
  grid: ReactNode;
  sidebar: ReactNode;
}) {
  return (
    <main
      className="scrolly flex min-h-0 flex-1 flex-col overflow-auto"
      data-screen="student-home"
    >
      <div className="order-1 px-[16px] py-[20px]">{grid}</div>
      {sidebar}
    </main>
  );
}

function DesktopHome({
  grid,
  sidebar,
  sidebarWidth,
}: {
  grid: ReactNode;
  sidebar: ReactNode;
  sidebarWidth: string;
}) {
  return (
    <main
      className="grid min-h-0 flex-1 [grid-template-areas:'chats_main']"
      style={{ gridTemplateColumns: `${sidebarWidth} minmax(0,1fr)` }}
      data-screen="student-home"
    >
      {sidebar}
      <div className="scrolly overflow-auto p-[clamp(20px,3vw,40px)] [grid-area:main]">
        {grid}
      </div>
    </main>
  );
}

/** Student landing screen: chats rail beside the topic grid (stacks on mobile). */
export function StudentHome({
  chat,
  name,
  initials,
  bp,
  onProfile,
  onPerformance,
  onLogout,
}: StudentHomeProps) {
  const mobile = bp === "mobile";
  const sidebarWidth = bp === "tablet" ? "268px" : "300px";
  const grid = (
    <TopicGrid
      name={name}
      initials={initials}
      onOpenTopic={chat.openTopic}
      onProfile={onProfile}
      onPerformance={onPerformance}
      onLogout={onLogout}
    />
  );
  const sidebar = (
    <ChatsSidebar
      chats={chat.state.chats}
      order={chat.state.order}
      onOpenChat={chat.openChat}
      className={
        mobile
          ? "order-2 border-t border-line bg-paper2 p-[16px]"
          : "overflow-auto border-r border-line bg-paper px-[14px] py-[18px] [grid-area:chats]"
      }
    />
  );

  return mobile ? (
    <MobileHome grid={grid} sidebar={sidebar} />
  ) : (
    <DesktopHome grid={grid} sidebar={sidebar} sidebarWidth={sidebarWidth} />
  );
}
