import CharacterDesigner from "@/components/CharacterDesigner";
import { requireDashboardSession } from "@/lib/dashboard-auth";

export default async function CharactersPage() {
  const { profile } = await requireDashboardSession();
  const allowClass =
    profile.role === "teacher" || profile.role === "admin";

  return (
    <div className="p-6">
      <h1 className="mb-2 text-2xl font-bold text-zinc-900 dark:text-zinc-50">
        Lesson Characters
      </h1>
      <p className="mb-6 text-sm text-zinc-500">
        Create a unique tutor mascot for lessons and the AI agent.
      </p>
      <CharacterDesigner allowClassPublish={allowClass} />
    </div>
  );
}
