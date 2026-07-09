import { Avatar, Modal, StatCard } from "@/components";
import { fullName } from "../data/student";
import type { PerformanceDTO, ProfileDTO } from "../api/student";
import { usePerformance, useProfile } from "../hooks/useMeData";
import type { ModalKind } from "../types";

interface StudentModalProps {
  modal: ModalKind;
  onClose: () => void;
  name: string;
  initials: string;
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3 rounded-sm bg-paper2 px-[14px] py-[11px]">
      <span className="text-[13px] text-ink2">{label}</span>
      <span className="text-[13px] font-semibold">{value}</span>
    </div>
  );
}

interface ProfileView {
  displayName: string;
  roleLine: string;
  initials: string;
  email: string;
  since: string;
  subjects: string;
}

function profileView(
  profile: ProfileDTO | null,
  name: string,
  initials: string,
): ProfileView {
  if (!profile) {
    return {
      displayName: fullName(name),
      roleLine: "Student",
      initials,
      email: "—",
      since: "—",
      subjects: "0",
    };
  }
  const grade = profile.grade ? ` · ${profile.grade}` : "";
  return {
    displayName: profile.full_name,
    roleLine: `${profile.role_label}${grade}`,
    initials: profile.initials,
    email: profile.email,
    since: profile.member_since,
    subjects: String(profile.subjects_available),
  };
}

function ProfileBody({
  profile,
  name,
  initials,
}: {
  profile: ProfileDTO | null;
  name: string;
  initials: string;
}) {
  const v = profileView(profile, name, initials);
  return (
    <div className="flex flex-col items-center gap-[14px] px-[22px] py-6 text-center">
      <Avatar initials={v.initials} gradient="violet" size={74} display />
      <div>
        <div className="font-display text-[20px] font-extrabold">
          {v.displayName}
        </div>
        <div className="mt-[2px] text-[13px] text-ink2">{v.roleLine}</div>
      </div>
      <div className="mt-1 flex w-full flex-col gap-[6px]">
        <DetailRow label="Email" value={v.email} />
        <DetailRow label="Member since" value={v.since} />
        <DetailRow label="Subjects available" value={v.subjects} />
      </div>
    </div>
  );
}

function PerformanceBody({ perf }: { perf: PerformanceDTO | null }) {
  const stats = perf?.stats ?? [];
  return (
    <div className="px-[18px] py-5">
      <div className="grid grid-cols-2 gap-[10px]">
        {stats.map((stat) => (
          <StatCard
            key={stat.key}
            value={stat.value}
            label={stat.label}
            size="md"
            background="paper2"
            valueClassName={stat.value_class}
          />
        ))}
      </div>
      {perf?.insight.text && (
        <div className="mt-[14px] rounded-sm border border-green-s bg-green-s2 px-[14px] py-3 text-[12.5px] leading-[1.5] text-green-d">
          {perf.insight.text}
        </div>
      )}
    </div>
  );
}

/** Profile / performance dialog for the student account menu (live from `/me/*`). */
export function StudentModal({
  modal,
  onClose,
  name,
  initials,
}: StudentModalProps) {
  const profile = useProfile(modal === "profile");
  const perf = usePerformance(modal === "performance");
  return (
    <Modal
      open={modal !== null}
      onClose={onClose}
      title={modal === "performance" ? "Your performance" : "Your profile"}
    >
      {modal === "performance" ? (
        <PerformanceBody perf={perf} />
      ) : (
        <ProfileBody profile={profile} name={name} initials={initials} />
      )}
    </Modal>
  );
}
