import { topicById } from "../data/topics";
import { useTopics } from "../hooks/useTopics";
import type { MiraChat } from "../hooks/useMiraChat";
import { ChatHeader } from "./ChatHeader";
import { Composer } from "./Composer";
import { CompletionBanner } from "./CompletionBanner";
import { MessageList } from "./messages/MessageList";

interface ChatViewProps {
  chat: MiraChat;
}

/** Single-conversation screen: header, transcript, and composer/banner. */
export function ChatView({ chat }: ChatViewProps) {
  const { state } = chat;
  const topics = useTopics();
  const topic =
    topics.find((t) => t.id === state.topicId) ?? topicById(state.topicId);

  return (
    <main className="flex min-h-0 flex-1 flex-col" data-screen="student-chat">
      <ChatHeader
        topic={topic}
        status={state.status}
        title={state.title}
        onBack={chat.goHome}
      />
      <MessageList
        messages={state.messages}
        typing={state.typing}
        status={state.status}
      />
      <div className="border-t border-line bg-paper px-[clamp(14px,2.4vw,26px)] pb-[14px] pt-[12px]">
        <div className="mx-auto max-w-[760px]">
          {state.error && (
            <div className="mb-[11px] rounded-lg border border-coral-s bg-coral-s px-[13px] py-[10px] text-[12.5px] text-coral-d">
              {state.error}
            </div>
          )}
          {state.locked ? (
            <CompletionBanner onNewChat={() => chat.openTopic(state.topicId)} />
          ) : (
            <Composer onSend={chat.sendMessage} />
          )}
        </div>
      </div>
    </main>
  );
}
