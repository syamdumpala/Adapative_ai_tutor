import { Badge, GlyphTile } from "@/components";
import { cn } from "@/lib/cn";
import { topicById } from "../data/topics";
import { useTopics } from "../hooks/useTopics";
import type { ChatSummary } from "../state/chatHelpers";
import type { Topic } from "../types";

interface ChatsSidebarProps {
  chats: Record<string, ChatSummary>;
  order: string[];
  onOpenChat: (id: string) => void;
  className?: string;
}

function ChatItem({
  chat,
  topics,
  onClick,
}: {
  chat: ChatSummary;
  topics: Topic[];
  onClick: () => void;
}) {
  const topic =
    topics.find((t) => t.id === chat.topicId) ?? topicById(chat.topicId);
  const pending = chat.status === "pending";
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-[10px] rounded-[12px] border border-line bg-card px-[11px] py-[9px] text-left shadow-soft transition hover:translate-x-[2px] hover:border-line2",
        pending && "border-l-[3px] border-l-amber",
      )}
    >
      <GlyphTile glyph={topic.glyph} tone={topic.tone} size={32} />
      <div className="min-w-0 flex-1 text-left">
        <div className="truncate text-[13px] font-semibold text-ink">
          {chat.title || topic.name}
        </div>
        <div className="truncate text-[11px] text-ink3">
          {topic.name} · {pending ? "in progress" : "resolved"}
        </div>
      </div>
      <Badge
        tone={pending ? "amberSolid" : "green"}
        pulse={pending}
        className="text-[9.5px]"
      >
        {pending ? "Pending" : "Done"}
      </Badge>
    </button>
  );
}

/** "Your chats" rail: seeded + live conversations across every topic. */
export function ChatsSidebar({
  chats,
  order,
  onOpenChat,
  className,
}: ChatsSidebarProps) {
  const topics = useTopics();
  const ids = order.filter((id) => chats[id]);
  const pending = ids.filter((id) => chats[id]!.status === "pending").length;
  const resolved = ids.filter((id) => chats[id]!.status === "completed").length;
  const meta = ids.length
    ? `${pending} in progress · ${resolved} resolved`
    : "Nothing yet — start one on the right";

  return (
    <aside className={cn("scrolly flex flex-col", className)}>
      <div className="px-1 pb-3 pt-[2px]">
        <div className="font-display text-[16px] font-bold">Your chats</div>
        <div className="mt-[3px] text-[11.5px] text-ink2">{meta}</div>
      </div>
      <div className="flex flex-col gap-[7px]">
        {ids.map((id) => (
          <ChatItem
            key={id}
            chat={chats[id]!}
            topics={topics}
            onClick={() => onOpenChat(id)}
          />
        ))}
      </div>
      {ids.length === 0 && (
        <div className="px-2 py-4 text-[12.5px] leading-normal text-ink3">
          No chats yet. Pick a topic to start one — it shows up here once you
          ask your first question.
        </div>
      )}
    </aside>
  );
}
