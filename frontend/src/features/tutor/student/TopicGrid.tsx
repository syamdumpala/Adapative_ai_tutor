import { useTopics } from "../hooks/useTopics";
import { ProfileMenu } from "./ProfileMenu";
import { TopicCard } from "./TopicCard";

interface TopicGridProps {
  name: string;
  initials: string;
  onOpenTopic: (id: string) => void;
  onProfile: () => void;
  onPerformance: () => void;
  onLogout: () => void;
}

/** Topics header (greeting + account menu) over the topic card grid. */
export function TopicGrid({
  name,
  initials,
  onOpenTopic,
  onProfile,
  onPerformance,
  onLogout,
}: TopicGridProps) {
  const topics = useTopics();
  return (
    <>
      <div className="mb-[clamp(18px,2.6vw,30px)] flex animate-fade-up flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="mb-[9px] font-mono text-[10px] uppercase tracking-[0.14em] text-ink3">
            Topics
          </div>
          <h1 className="text-[clamp(25px,4vw,38px)] font-extrabold">
            Hi, {name}. Pick a topic to begin.
          </h1>
          <p className="mt-2 max-w-[48ch] text-[14px] text-ink2">
            Open any topic and just ask — Mira guides you with hints, never
            straight answers.
          </p>
        </div>
        <ProfileMenu
          name={name}
          initials={initials}
          onProfile={onProfile}
          onPerformance={onPerformance}
          onLogout={onLogout}
        />
      </div>
      <div className="grid gap-[clamp(12px,1.6vw,18px)] [grid-template-columns:repeat(auto-fill,minmax(min(100%,240px),1fr))]">
        {topics.map((topic) => (
          <TopicCard
            key={topic.id}
            topic={topic}
            onClick={() => onOpenTopic(topic.id)}
          />
        ))}
      </div>
    </>
  );
}
