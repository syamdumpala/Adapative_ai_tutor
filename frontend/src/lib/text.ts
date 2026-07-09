/** First `count` words of `text`, with an ellipsis appended when it was longer. */
export function truncateWords(text: string, count: number): string {
  const trimmed = text.trim();
  const words = trimmed.split(/\s+/);
  if (words.length <= count) return trimmed;
  return `${words.slice(0, count).join(" ")}…`;
}
