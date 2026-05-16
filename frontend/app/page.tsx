import MemeGenerator from "@/components/MemeGenerator";

export default function Home() {
  return (
    <div className="flex min-h-full flex-1 flex-col items-center justify-center bg-gradient-to-b from-violet-50/80 to-white px-4 py-16 dark:from-zinc-950 dark:to-zinc-900">
      <MemeGenerator />
    </div>
  );
}
