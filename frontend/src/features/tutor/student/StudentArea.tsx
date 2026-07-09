import type { Breakpoint } from "@/hooks/useResponsive";
import type { MiraChat } from "../hooks/useMiraChat";
import type { StudentView } from "../types";
import { StudentAnalytics } from "./analytics/StudentAnalytics";
import { ChatView } from "./ChatView";
import { StudentHome } from "./StudentHome";

interface StudentAreaProps {
  chat: MiraChat;
  name: string;
  initials: string;
  bp: Breakpoint;
  studentView: StudentView;
  onProfile: () => void;
  onPerformance: () => void;
  onAnalytics: () => void;
  onBackHome: () => void;
  onLogout: () => void;
}

/** Student side of the app: analytics page, home (no chat), or the open chat. */
export function StudentArea({
  chat,
  name,
  initials,
  bp,
  studentView,
  onProfile,
  onPerformance,
  onAnalytics,
  onBackHome,
  onLogout,
}: StudentAreaProps) {
  if (studentView === "analytics") {
    return <StudentAnalytics name={name} onBack={onBackHome} />;
  }
  if (chat.state.activeChatId === null) {
    return (
      <StudentHome
        chat={chat}
        name={name}
        initials={initials}
        bp={bp}
        onProfile={onProfile}
        onPerformance={onPerformance}
        onAnalytics={onAnalytics}
        onLogout={onLogout}
      />
    );
  }
  return <ChatView chat={chat} />;
}
