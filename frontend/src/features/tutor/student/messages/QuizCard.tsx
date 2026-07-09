import { Badge } from "@/components";
import { cn } from "@/lib/cn";
import type {
  ConfidenceValue,
  QuizData,
  QuizOption,
  QuizSegment,
} from "../../types";

const PILLS: [ConfidenceValue, string][] = [
  ["sure", "Sure"],
  ["think", "Think so"],
  ["guess", "Guessing"],
];

interface OptionAppearance {
  border: string;
  bg: string;
  mark: string;
  markColor: string;
  dim: boolean;
}

function optionAppearance(
  option: QuizOption,
  quiz: QuizData,
  index: number,
): OptionAppearance {
  const isSelected = quiz.selected === index;
  if (quiz.answered && option.correct) {
    return {
      border: "border-green",
      bg: "bg-green-s2",
      mark: "✓",
      markColor: "text-green-d",
      dim: false,
    };
  }
  if (quiz.answered && isSelected) {
    return {
      border: "border-coral",
      bg: "bg-coral-s",
      mark: "✕",
      markColor: "text-coral-d",
      dim: false,
    };
  }
  return {
    border: "border-line",
    bg: "bg-card",
    mark: "",
    markColor: "text-ink3",
    dim: quiz.answered,
  };
}

function OptionBars({ segs }: { segs: QuizSegment[] }) {
  return (
    <div className="flex h-[22px] flex-1 gap-[2px] overflow-hidden rounded-[7px]">
      {segs.map((seg, index) => (
        <div
          key={index}
          style={{ flex: seg.flex }}
          className={seg.on ? "bg-green" : "bg-wash"}
        />
      ))}
    </div>
  );
}

function QuizOptionButton({
  option,
  quiz,
  index,
  onAnswer,
}: {
  option: QuizOption;
  quiz: QuizData;
  index: number;
  onAnswer: (idx: number) => void;
}) {
  const look = optionAppearance(option, quiz, index);
  return (
    <button
      type="button"
      disabled={quiz.answered}
      onClick={() => onAnswer(index)}
      className={cn(
        "flex items-center gap-[12px] rounded-[12px] border-[1.5px] px-[14px] py-[11px] text-left transition",
        look.border,
        look.bg,
        look.dim && "opacity-50",
        quiz.answered ? "cursor-default" : "cursor-pointer",
      )}
    >
      {option.type === "bar" ? (
        <OptionBars segs={option.segs ?? []} />
      ) : (
        <span className="flex-1 text-[14px] font-semibold text-ink">
          {option.label}
        </span>
      )}
      <span
        className={cn(
          "w-5 text-center text-[15px] font-extrabold",
          look.markColor,
        )}
      >
        {look.mark}
      </span>
    </button>
  );
}

function ConfidenceRow({
  quiz,
  onRate,
}: {
  quiz: QuizData;
  onRate: (value: ConfidenceValue) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-[8px]">
      <span
        className={cn(
          "text-[11.5px] font-semibold",
          quiz.needConf ? "text-coral-d" : "text-ink2",
        )}
      >
        How sure are you?
      </span>
      {PILLS.map(([value, label]) => (
        <button
          key={value}
          type="button"
          onClick={() => onRate(value)}
          className={cn(
            "h-[32px] rounded-full px-[13px] text-[12px] font-semibold transition",
            quiz.confidence === value
              ? "bg-amber text-white shadow-soft"
              : "border border-line bg-paper2 text-ink2",
          )}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

interface QuizCardProps {
  quiz: QuizData;
  celebrate: boolean;
  onRate: (value: ConfidenceValue) => void;
  onAnswer: (idx: number) => void;
}

/** Confidence-gated practice question with segmented-bar or label options. */
export function QuizCard({ quiz, celebrate, onRate, onAnswer }: QuizCardProps) {
  return (
    <div className="relative flex flex-col gap-[12px]">
      {quiz.answered && quiz.correct && celebrate && (
        <span
          aria-hidden
          style={{ animation: "burst 0.6s ease-out forwards" }}
          className="pointer-events-none absolute right-3 top-1 h-6 w-6 rounded-full bg-green/40"
        />
      )}
      <div className="flex items-center justify-between gap-[10px]">
        <Badge tone="green" mono>
          Practice · {quiz.concept}
        </Badge>
        <span className="font-mono text-[9.5px] uppercase tracking-[0.1em] text-ink3">
          {quiz.diff}
        </span>
      </div>
      <div className="font-display text-[16px] font-bold leading-[1.25]">
        {quiz.text}
      </div>
      <ConfidenceRow quiz={quiz} onRate={onRate} />
      <div className="flex flex-col gap-[8px]">
        {quiz.options.map((option, index) => (
          <QuizOptionButton
            key={index}
            option={option}
            quiz={quiz}
            index={index}
            onAnswer={onAnswer}
          />
        ))}
      </div>
      {quiz.answered && (
        <div
          className={cn(
            "rounded-[9px] px-[11px] py-[8px] text-[12px] font-semibold",
            quiz.correct ? "bg-green-s text-green-d" : "bg-amber-s text-amber",
          )}
        >
          {quiz.correct
            ? "Correct · confidence logged → mastery +"
            : "Let’s retry — memory not penalized for one miss."}
        </div>
      )}
    </div>
  );
}
