import { subjectById } from "../data/subjects";
import type { MiraChat } from "../hooks/useMiraChat";
import { ChatHeader } from "./ChatHeader";
import { Composer } from "./Composer";
import { CompletionBanner } from "./CompletionBanner";
import { MessageList } from "./messages/MessageList";

interface ChatViewProps {
  chat: MiraChat;
  celebrate: boolean;
  onToTeacher: () => void;
}

/** Single-conversation screen: header, transcript, and composer/banner. */
export function ChatView({ chat, celebrate, onToTeacher }: ChatViewProps) {
  const { state } = chat;
  const subject = subjectById(state.subjectId);

  return (
    <main className="flex min-h-0 flex-1 flex-col" data-screen="student-chat">
      <ChatHeader
        subject={subject}
        status={state.status}
        title={state.title}
        onBack={chat.goHome}
      />
      <MessageList
        messages={state.messages}
        typing={state.typing}
        status={state.status}
        celebrate={celebrate}
        onRate={chat.rateConfidence}
        onAnswer={chat.answerQuiz}
      />
      <div className="border-t border-line bg-paper px-[clamp(14px,2.4vw,26px)] pb-[14px] pt-[12px]">
        <div className="mx-auto max-w-[760px]">
          {state.locked ? (
            <CompletionBanner
              onNewChat={() => chat.openSubject(state.subjectId)}
              onToTeacher={onToTeacher}
            />
          ) : (
            <Composer
              controls={state.controls}
              hintRung={state.hintRung}
              leakChecks={state.leakChecks}
              onControl={chat.sendControl}
              onSend={chat.sendMessage}
            />
          )}
        </div>
      </div>
    </main>
  );
}
