import AdminContactInbox from "@/components/dashboard/AdminContactInbox";
import type { ContactSubmissionRow } from "@/lib/api";
import { getServerAccessToken } from "@/lib/supabase/server-auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default async function AdminContactPage() {
  const token = await getServerAccessToken();
  let submissions: ContactSubmissionRow[] = [];
  let error: string | null = null;

  if (token) {
    try {
      const res = await fetch(`${API_BASE}/admin/contact-submissions`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      if (res.ok) {
        submissions = await res.json();
      } else {
        error = "Failed to load contact submissions.";
      }
    } catch {
      error = "Failed to load contact submissions.";
    }
  }

  return (
    <>
      <header className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">Contact inbox</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Messages from the public Contact Us form, stored in the database.
        </p>
      </header>
      {error ? (
        <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </p>
      ) : (
        <AdminContactInbox initialSubmissions={submissions} />
      )}
    </>
  );
}
