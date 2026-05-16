import { redirect } from "next/navigation";
import { fetchMe } from "@/lib/api-server";
import { getServerAccessToken } from "@/lib/supabase/server-auth";
import type { AppRole } from "@/lib/roles";
import { normalizeRole } from "@/lib/roles";

export async function requireDashboardRole(
  allowed: AppRole[],
): Promise<{ role: AppRole; token: string }> {
  const token = await getServerAccessToken();
  if (!token) redirect("/login");

  let role: AppRole = "student";
  try {
    const me = await fetchMe(token);
    role = normalizeRole(me.role);
  } catch {
    redirect("/login");
  }

  if (!allowed.includes(role)) {
    redirect("/dashboard");
  }

  return { role, token };
}

export async function requireDashboardSession(): Promise<{
  role: AppRole;
  token: string;
  profile: Awaited<ReturnType<typeof fetchMe>>;
}> {
  const token = await getServerAccessToken();
  if (!token) redirect("/login");

  try {
    const profile = await fetchMe(token);
    return { role: normalizeRole(profile.role), token, profile };
  } catch {
    redirect("/login");
  }
}
