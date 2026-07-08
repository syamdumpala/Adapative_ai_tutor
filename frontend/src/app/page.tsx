export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center bg-zinc-50 px-6 font-sans dark:bg-black">
      <main className="flex w-full max-w-2xl flex-col gap-6 text-center sm:text-left">
        <h1 className="text-3xl font-semibold tracking-tight text-black dark:text-zinc-50">
          Adaptive AI Tutor
        </h1>
        <p className="text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          Frontend scaffold. Read <code>RULES.md</code> and the{" "}
          <code>docs/</code> folder before contributing.
        </p>
      </main>
    </div>
  );
}
