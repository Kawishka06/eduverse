import { getApiBase } from "@/lib/api-base";
import { createClient } from "@/lib/supabase/client";

const API_BASE = getApiBase();

export async function getAccessToken(): Promise<string | null> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token ?? null;
}

export async function syncProfile(token: string) {
  const res = await fetch(`${API_BASE}/sync`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? "Failed to sync profile");
  }
  return res.json();
}
