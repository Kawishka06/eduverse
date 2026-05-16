"use client";

import { useState } from "react";
import type { ContactSubmissionRow } from "@/lib/api";
import {
  fetchContactSubmissions,
  updateContactSubmissionStatus,
} from "@/lib/api";

const STATUS_FILTERS = ["all", "new", "read", "resolved"] as const;

export default function AdminContactInbox({
  initialSubmissions,
}: {
  initialSubmissions: ContactSubmissionRow[];
}) {
  const [submissions, setSubmissions] = useState(initialSubmissions);
  const [filter, setFilter] = useState<string>("all");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function reload(status: string) {
    setLoading(true);
    try {
      const rows = await fetchContactSubmissions(
        status === "all" ? undefined : status,
      );
      setSubmissions(rows);
    } catch {
      alert("Failed to load submissions");
    } finally {
      setLoading(false);
    }
  }

  async function setStatus(id: string, status: "new" | "read" | "resolved") {
    setBusyId(id);
    try {
      await updateContactSubmissionStatus(id, status);
      setSubmissions((prev) =>
        prev.map((s) => (s.id === id ? { ...s, status } : s)),
      );
    } catch {
      alert("Failed to update status");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <label className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
          Filter
          <select
            value={filter}
            onChange={async (e) => {
              const v = e.target.value;
              setFilter(v);
              await reload(v);
            }}
            className="ml-2 rounded-lg border border-zinc-200 bg-white px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            disabled={loading}
          >
            {STATUS_FILTERS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        {loading && (
          <span className="text-xs text-zinc-500">Loading…</span>
        )}
      </div>

      {submissions.length === 0 ? (
        <p className="text-sm text-zinc-500">No contact submissions yet.</p>
      ) : (
        <ul className="space-y-4">
          {submissions.map((s) => (
            <li
              key={s.id}
              className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800"
            >
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p className="font-semibold">{s.subject}</p>
                  <p className="text-sm text-zinc-600 dark:text-zinc-400">
                    {s.name} · {s.email} · {s.category}
                  </p>
                </div>
                <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium capitalize dark:bg-zinc-800">
                  {s.status}
                </span>
              </div>
              <p className="mt-3 whitespace-pre-wrap text-sm text-zinc-700 dark:text-zinc-300">
                {s.message}
              </p>
              <p className="mt-2 text-xs text-zinc-400">
                {new Date(s.created_at).toLocaleString()}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {(["read", "resolved"] as const).map((st) => (
                  <button
                    key={st}
                    type="button"
                    disabled={busyId === s.id || s.status === st}
                    onClick={() => setStatus(s.id, st)}
                    className="rounded-lg border border-zinc-200 px-3 py-1 text-xs font-medium disabled:opacity-50 dark:border-zinc-700"
                  >
                    Mark {st}
                  </button>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
