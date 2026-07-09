import { Badge, GlyphTile } from "@/components";
import { cn } from "@/lib/cn";
import { subjectById } from "../data/subjects";
import type { Chat } from "../types";

interface ChatsSidebarProps {
  chats: Record<string, Chat>;
  order: string[];
  onOpenChat: (id: string) => void;
  className?: string;
}

function ChatItem({ chat, onClick }: { chat: Chat; onClick: () => void }) {
  const subject = subjectById(chat.subjectId);
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
      <GlyphTile glyph={subject.glyph} tone={subject.tone} size={32} />
      <div className="min-w-0 flex-1 text-left">
        <div className="truncate text-[13px] font-semibold text-ink">
          {chat.title || subject.name}
        </div>
        <div className="truncate text-[11px] text-ink3">
          {subject.name} · {pending ? "in progress" : "resolved"}
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

/** "Your chats" rail: seeded + live conversations across every subject. */
export function ChatsSidebar({
  chats,
  order,
  onOpenChat,
  className,
}: ChatsSidebarProps) {
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
          <ChatItem key={id} chat={chats[id]!} onClick={() => onOpenChat(id)} />
        ))}
      </div>
      {ids.length === 0 && (
        <div className="px-2 py-4 text-[12.5px] leading-normal text-ink3">
          No chats yet. Pick a subject to start one — it shows up here once you
          ask your first question.
        </div>
      )}
    </aside>
  );
}
