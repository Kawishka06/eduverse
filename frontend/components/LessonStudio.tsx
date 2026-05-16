"use client";

import { useCallback, useEffect, useState } from "react";
import {
  fetchCharacters,
  fetchMaterials,
  getLessonVideoJob,
  savePost,
  startLessonVideo,
  uploadMaterial,
  type LessonCharacter,
  type LessonMaterial,
  type LessonVideoJob,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

function LessonSceneVideo({
  jobId,
  sceneIndex,
  url,
}: {
  jobId: string;
  sceneIndex: number;
  url: string;
}) {
  const [src, setSrc] = useState<string>(url);
  const needsAuth =
    url.includes("/lesson-video/") && url.includes("/scenes/");

  useEffect(() => {
    if (!needsAuth) {
      setSrc(url);
      return;
    }
    let objectUrl: string | null = null;
    (async () => {
      const token = await getAccessToken();
      if (!token) return;
      const res = await fetch(
        `/api/lesson-video/${jobId}/scenes/${sceneIndex}/file`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      if (!res.ok) return;
      const blob = await res.blob();
      objectUrl = URL.createObjectURL(blob);
      setSrc(objectUrl);
    })();
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [jobId, sceneIndex, url, needsAuth]);

  return (
    <video src={src} controls playsInline className="w-full rounded-lg" />
  );
}

export default function LessonStudio() {
  const [materials, setMaterials] = useState<LessonMaterial[]>([]);
  const [characters, setCharacters] = useState<LessonCharacter[]>([]);
  const [materialId, setMaterialId] = useState("");
  const [characterId, setCharacterId] = useState("");
  const [job, setJob] = useState<LessonVideoJob | null>(null);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const load = useCallback(async () => {
    try {
      const [m, c] = await Promise.all([fetchMaterials(), fetchCharacters()]);
      setMaterials(m);
      setCharacters(c);
      if (m.length && !materialId) setMaterialId(m[0].id);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to load";
      setError(msg === "Failed to fetch" ? "Cannot reach the server. Is the backend running?" : msg);
    }
  }, [materialId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!job || job.status === "completed" || job.status === "failed") return;
    const t = setInterval(async () => {
      try {
        const updated = await getLessonVideoJob(job.job_id);
        setJob(updated);
      } catch {
        /* ignore poll errors */
      }
    }, 3000);
    return () => clearInterval(t);
  }, [job]);

  async function onUpload(file: File) {
    setUploading(true);
    setError(null);
    try {
      const m = await uploadMaterial(file);
      setMaterials((prev) => [m, ...prev]);
      setMaterialId(m.id);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Upload failed";
      setError(msg === "Failed to fetch" ? "Cannot reach the server. Is the backend running?" : msg);
    } finally {
      setUploading(false);
    }
  }

  async function onGenerate() {
    if (!materialId) return;
    setGenerating(true);
    setError(null);
    setSaved(false);
    try {
      const started = await startLessonVideo(materialId, characterId || null);
      setJob(started);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setGenerating(false);
    }
  }

  async function onSaveToLibrary() {
    const url =
      job?.playlist_url ||
      job?.scenes?.[0]?.video_url ||
      job?.scenes?.[0]?.image_url;
    if (!url) return;
    try {
      await savePost(url, job?.title || "Lesson video", "video");
      setSaved(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <section className="rounded-2xl border border-indigo-500/20 bg-white/90 p-6 dark:bg-zinc-900/90">
        <h2 className="font-semibold text-zinc-900 dark:text-zinc-50">Upload material</h2>
        <p className="mt-1 text-sm text-zinc-500">
          PDF, .txt, .md, or images. Text is read automatically for lesson scripts.
        </p>
        <input
          type="file"
          accept=".pdf,.txt,.md,.markdown,.csv,.json,text/*,image/*"
          disabled={uploading}
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onUpload(f);
          }}
          className="mt-3 block w-full text-sm"
        />
      </section>

      <section className="rounded-2xl border border-zinc-200 p-6 dark:border-zinc-700">
        <label className="block text-sm font-medium">Material</label>
        <select
          value={materialId}
          onChange={(e) => setMaterialId(e.target.value)}
          className="mt-1 w-full rounded-lg border px-3 py-2 text-sm dark:bg-zinc-800"
        >
          {materials.map((m) => (
            <option key={m.id} value={m.id}>
              {m.filename}
              {m.extracted_text
                ? ` ✓ (${Math.min(m.extracted_text.length, 9999)} chars)`
                : " (no text yet — re-upload or pick another)"}
            </option>
          ))}
        </select>

        <label className="mt-4 block text-sm font-medium">Character (optional)</label>
        <select
          value={characterId}
          onChange={(e) => setCharacterId(e.target.value)}
          className="mt-1 w-full rounded-lg border px-3 py-2 text-sm dark:bg-zinc-800"
        >
          <option value="">No character</option>
          {characters.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>

        <button
          type="button"
          onClick={onGenerate}
          disabled={generating || !materialId}
          className="mt-4 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {generating ? "Starting…" : "Generate animated lesson video"}
        </button>
      </section>

      {job && (
        <section className="rounded-2xl border border-zinc-200 p-6 dark:border-zinc-700">
          <p className="text-sm font-medium">
            Status: {job.status} · {job.progress}%
          </p>
          {job.phase && job.status === "processing" && (
            <p className="mt-1 text-sm text-zinc-500">{job.phase}</p>
          )}
          {job.status === "processing" && (
            <p className="mt-2 text-xs text-zinc-400">
              Building animated clips with your character&apos;s voice (about 2–4 min per scene).
              Requires ffmpeg on the server to merge audio into video.
            </p>
          )}
          {job.error && <p className="mt-1 text-sm text-red-600">{job.error}</p>}
          {job.title && (
            <h3 className="mt-2 text-lg font-semibold">{job.title}</h3>
          )}
          <div className="mt-4 space-y-4">
            {job.scenes?.map((scene, i) => (
              <div key={i} className="rounded-lg border p-3 dark:border-zinc-600">
                <p className="font-medium">{scene.title}</p>
                <p className="mt-1 text-xs italic text-zinc-500">{scene.narration}</p>
                {scene.video_url && (
                  <div className="mt-3">
                    <p className="mb-1 text-xs font-medium text-indigo-600 dark:text-indigo-400">
                      {scene.video_url.includes("/scenes/")
                        ? "Lesson video (animated + voice)"
                        : "Animated clip"}
                    </p>
                    <LessonSceneVideo
                      jobId={job.job_id}
                      sceneIndex={i}
                      url={scene.video_url}
                    />
                  </div>
                )}
                {scene.audio_url && !scene.video_url?.includes("/scenes/") && (
                  <div className="mt-3">
                    <p className="mb-1 text-xs font-medium text-amber-600 dark:text-amber-400">
                      Voice only — waiting for video or install ffmpeg on the server
                    </p>
                    <audio src={scene.audio_url} controls className="w-full" />
                  </div>
                )}
                {scene.image_url && !scene.video_url && (
                  <img
                    src={scene.image_url}
                    alt={scene.title}
                    className="mt-2 w-full rounded-lg"
                  />
                )}
              </div>
            ))}
          </div>
          {job.status === "completed" && (
            <button
              type="button"
              onClick={onSaveToLibrary}
              className="mt-4 text-sm text-indigo-600 hover:underline"
            >
              {saved ? "Saved to library" : "Save first clip to library"}
            </button>
          )}
        </section>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
