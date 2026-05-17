"use client";

import { useMemo, useState } from "react";
import { lessonVideoApiPath, parseLessonVideoJobId } from "@/lib/lesson-video-url";

type Props = {
  jobId: string;
  url: string;
  poster?: string | null;
  className?: string;
};

export default function LessonVideoPlayer({
  jobId,
  url,
  poster,
  className = "w-full rounded-lg bg-zinc-900",
}: Props) {
  const resolvedJobId = parseLessonVideoJobId(url) ?? jobId;
  const isLessonFile =
    url.includes("/lesson-video/") &&
    (url.includes("/file") || url.includes("/scenes/"));

  const src = useMemo(() => {
    if (isLessonFile) {
      return url.includes("/scenes/")
        ? `/api/lesson-video/${resolvedJobId}/scenes/0/file`
        : lessonVideoApiPath(resolvedJobId);
    }
    return url;
  }, [isLessonFile, resolvedJobId, url]);

  const [loadError, setLoadError] = useState<string | null>(null);

  return (
    <div>
      {loadError ? (
        <p className="mb-2 text-sm text-amber-700 dark:text-amber-300">{loadError}</p>
      ) : null}
      <video
        key={src}
        src={src}
        poster={poster ?? undefined}
        controls
        playsInline
        preload="metadata"
        className={className}
        onError={() => {
          // #region agent log
          fetch("http://127.0.0.1:7574/ingest/3c6afa58-30ac-4e5e-9854-7a3b8425de96", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Debug-Session-Id": "ba63c3",
            },
            body: JSON.stringify({
              sessionId: "ba63c3",
              location: "LessonVideoPlayer.tsx:onError",
              message: "video element error",
              data: { jobId: resolvedJobId, src },
              timestamp: Date.now(),
              hypothesisId: "H11",
              runId: "post-fix-2",
            }),
          }).catch(() => {});
          // #endregion
          setLoadError(
            "Could not play this video. Refresh the page or generate the lesson again.",
          );
        }}
        onLoadedData={() => setLoadError(null)}
      />
    </div>
  );
}
