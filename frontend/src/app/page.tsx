import { TutorApp } from "@/features/tutor/TutorApp";

interface HomeProps {
  searchParams: Promise<{ role?: string | string[] }>;
}

/** Mira Tutor entry point. `?role=teacher` opens the teacher dashboard. */
export default async function Home({ searchParams }: HomeProps) {
  const { role } = await searchParams;
  return <TutorApp initialRole={role === "teacher" ? "teacher" : "student"} />;
}
