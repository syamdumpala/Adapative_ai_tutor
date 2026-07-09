import type { Breakpoint } from "@/hooks/useResponsive";
import type { MiraChat } from "../hooks/useMiraChat";
import { ChatView } from "./ChatView";
import { StudentHome } from "./StudentHome";

interface StudentAreaProps {
  chat: MiraChat;
  name: string;
  initials: string;
  bp: Breakpoint;
  onProfile: () => void;
  onPerformance: () => void;
  onLogout: () => void;
}

/** Student side of the app; home when no chat is open, otherwise the chat. */
export function StudentArea({
  chat,
  name,
  initials,
  bp,
  onProfile,
  onPerformance,
  onLogout,
}: StudentAreaProps) {
  if (chat.state.activeChatId === null) {
    return (
      <StudentHome
        chat={chat}
        name={name}
        initials={initials}
        bp={bp}
        onProfile={onProfile}
        onPerformance={onPerformance}
        onLogout={onLogout}
      />
    );
  }
  return <ChatView chat={chat} />;
}
