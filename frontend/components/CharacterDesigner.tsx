"use client";

import { FormEvent, useEffect, useState } from "react";
import {
  createCharacter,
  deleteCharacter,
  fetchCharacters,
  type LessonCharacter,
} from "@/lib/api";

type Props = {
  allowClassPublish?: boolean;
};

export default function CharacterDesigner({ allowClassPublish = false }: Props) {
  const [characters, setCharacters] = useState<LessonCharacter[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    personality: "",
    teaching_style: "",
    visual_description: "",
    voice_style: "friendly",
    visibility: "personal" as "personal" | "class",
    class_tag: "",
  });

  async function load() {
    setLoading(true);
    try {
      setCharacters(await fetchCharacters());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await createCharacter({
        ...form,
        class_tag: form.class_tag || undefined,
        generate_art: true,
      });
      setForm({
        name: "",
        personality: "",
        teaching_style: "",
        visual_description: "",
        voice_style: "friendly",
        visibility: "personal",
        class_tag: "",
      });
      await load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Create failed";
      setError(msg === "Failed to fetch" ? "Cannot reach the server. Is the backend running?" : msg);
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(id: string) {
    if (!confirm("Delete this character?")) return;
    try {
      await deleteCharacter(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <section className="rounded-2xl border border-indigo-500/20 bg-white/90 p-6 shadow-lg dark:bg-zinc-900/90">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Design a lesson character
        </h2>
        <p className="mt-1 text-sm text-zinc-500">
          Describe your mascot — fal.ai generates unique reference art (not a preset avatar).
        </p>

        <form onSubmit={onSubmit} className="mt-4 space-y-3">
          <input
            required
            placeholder="Character name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800"
          />
          <textarea
            placeholder="Personality (e.g. bubbly, wise owl)"
            value={form.personality}
            onChange={(e) => setForm({ ...form, personality: e.target.value })}
            className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800"
            rows={2}
          />
          <textarea
            placeholder="Teaching style"
            value={form.teaching_style}
            onChange={(e) => setForm({ ...form, teaching_style: e.target.value })}
            className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800"
            rows={2}
          />
          <textarea
            required
            minLength={10}
            placeholder="Visual description (outfit, colors, species, vibe)"
            value={form.visual_description}
            onChange={(e) => setForm({ ...form, visual_description: e.target.value })}
            className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800"
            rows={3}
          />
          {allowClassPublish && (
            <>
              <select
                value={form.visibility}
                onChange={(e) =>
                  setForm({
                    ...form,
                    visibility: e.target.value as "personal" | "class",
                  })
                }
                className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800"
              >
                <option value="personal">Personal only</option>
                <option value="class">Publish to class</option>
              </select>
              <input
                placeholder="Class tag (optional)"
                value={form.class_tag}
                onChange={(e) => setForm({ ...form, class_tag: e.target.value })}
                className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800"
              />
            </>
          )}
          <button
            type="submit"
            disabled={saving}
            className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {saving ? "Generating…" : "Create & generate art"}
          </button>
        </form>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </section>

      <section>
        <h3 className="mb-3 font-medium text-zinc-800 dark:text-zinc-200">Your characters</h3>
        {loading ? (
          <p className="text-sm text-zinc-500">Loading…</p>
        ) : characters.length === 0 ? (
          <p className="text-sm text-zinc-500">No characters yet.</p>
        ) : (
          <ul className="space-y-4">
            {characters.map((c) => (
              <li
                key={c.id}
                className="flex gap-4 rounded-xl border border-zinc-200 p-4 dark:border-zinc-700"
              >
                {c.reference_image_url && (
                  <img
                    src={c.reference_image_url}
                    alt={c.name}
                    className="h-24 w-20 rounded-lg object-cover"
                  />
                )}
                <div className="flex-1">
                  <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                    {c.name}
                    {c.visibility === "class" && (
                      <span className="ml-2 text-xs text-indigo-600">class</span>
                    )}
                  </p>
                  <p className="mt-1 line-clamp-2 text-xs text-zinc-500">
                    {c.character_bible || c.visual_description}
                  </p>
                  <button
                    type="button"
                    onClick={() => onDelete(c.id)}
                    className="mt-2 text-xs text-red-600 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
