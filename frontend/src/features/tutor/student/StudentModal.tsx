import { Avatar, Modal, StatCard } from "@/components";
import { fullName } from "../data/student";
import type { ModalKind } from "../types";

interface StudentModalProps {
  modal: ModalKind;
  onClose: () => void;
  name: string;
  initials: string;
}

const PERF_STATS = [
  { value: "84%", label: "Recent accuracy", valueClassName: "text-green" },
  { value: "12", label: "Concepts mastered", valueClassName: "text-ink" },
  { value: "6", label: "Day streak", valueClassName: "text-violet" },
  {
    value: "1",
    label: "Misconception resolving",
    valueClassName: "text-amber",
  },
];

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3 rounded-sm bg-paper2 px-[14px] py-[11px]">
      <span className="text-[13px] text-ink2">{label}</span>
      <span className="text-[13px] font-semibold">{value}</span>
    </div>
  );
}

function ProfileBody({ name, initials }: { name: string; initials: string }) {
  return (
    <div className="flex flex-col items-center gap-[14px] px-[22px] py-6 text-center">
      <Avatar initials={initials} gradient="violet" size={74} display />
      <div>
        <div className="font-display text-[20px] font-extrabold">
          {fullName(name)}
        </div>
        <div className="mt-[2px] text-[13px] text-ink2">Student · Grade 5</div>
      </div>
      <div className="mt-1 flex w-full flex-col gap-[6px]">
        <DetailRow label="Email" value="maya.chen@school.edu" />
        <DetailRow label="Member since" value="Sep 2025" />
        <DetailRow label="Subjects available" value="6" />
      </div>
    </div>
  );
}

function PerformanceBody() {
  return (
    <div className="px-[18px] py-5">
      <div className="grid grid-cols-2 gap-[10px]">
        {PERF_STATS.map((stat) => (
          <StatCard
            key={stat.label}
            value={stat.value}
            label={stat.label}
            size="md"
            background="paper2"
            valueClassName={stat.valueClassName}
          />
        ))}
      </div>
      <div className="mt-[14px] rounded-sm border border-green-s bg-green-s2 px-[14px] py-3 text-[12.5px] leading-[1.5] text-green-d">
        Whole-number bias is <b>resolving</b> — keep practicing and it will be
        fully cleared soon.
      </div>
    </div>
  );
}

/** Profile / performance dialog for the student account menu. */
export function StudentModal({
  modal,
  onClose,
  name,
  initials,
}: StudentModalProps) {
  return (
    <Modal
      open={modal !== null}
      onClose={onClose}
      title={modal === "performance" ? "Your performance" : "Your profile"}
    >
      {modal === "performance" ? (
        <PerformanceBody />
      ) : (
        <ProfileBody name={name} initials={initials} />
      )}
    </Modal>
  );
}
