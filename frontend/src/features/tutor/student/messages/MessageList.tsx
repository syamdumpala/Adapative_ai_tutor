"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage, ChatStatus, ConfidenceValue } from "../../types";
import { MessageRow } from "./MessageRow";
import { TypingIndicator } from "./TypingIndicator";

interface MessageListProps {
  messages: ChatMessage[];
  typing: boolean;
  status: ChatStatus;
  celebrate: boolean;
  onRate: (msgId: number, value: ConfidenceValue) => void;
  onAnswer: (msgId: number, idx: number) => void;
}

/** Scrollable transcript; auto-sticks to the bottom as messages arrive. */
export function MessageList({
  messages,
  typing,
  status,
  celebrate,
  onRate,
  onAnswer,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages.length, typing]);

  const dayLabel =
    status === "completed" ? "Saved conversation" : "Live session · Today";

  return (
    <div
      ref={scrollRef}
      className="scrolly flex flex-1 flex-col gap-4 overflow-auto p-[clamp(16px,2.4vw,30px)]"
    >
      <div className="mx-auto flex w-full max-w-[760px] flex-col gap-4">
        <div className="pb-[6px] pt-[2px] text-center">
          <span className="rounded-full border border-line bg-paper2 px-3 py-[5px] font-mono text-[10px] uppercase tracking-[0.13em] text-ink3">
            {dayLabel}
          </span>
        </div>
        {messages.map((message) => (
          <MessageRow
            key={message.id}
            message={message}
            celebrate={celebrate}
            onRate={onRate}
            onAnswer={onAnswer}
          />
        ))}
        {typing && <TypingIndicator />}
      </div>
    </div>
  );
}
