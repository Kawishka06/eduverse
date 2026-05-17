import { backendUrl } from "@/lib/api-proxy";
import { getServerAccessToken } from "@/lib/supabase/server-auth";

type RouteContext = { params: Promise<{ jobId: string }> };

export const maxDuration = 120;

export async function GET(request: Request, context: RouteContext) {
  const { jobId } = await context.params;
  const authHeader = request.headers.get("authorization");
  const token =
    authHeader?.replace(/^Bearer\s+/i, "").trim() || (await getServerAccessToken());

  if (!token) {
    return new Response("Sign in required", { status: 401 });
  }

  try {
    const res = await fetch(backendUrl(`/ai/lesson-video/${jobId}/file`), {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      // #region agent log
      fetch("http://127.0.0.1:7574/ingest/3c6afa58-30ac-4e5e-9854-7a3b8425de96", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Debug-Session-Id": "ba63c3",
        },
        body: JSON.stringify({
          sessionId: "ba63c3",
          location: "api/lesson-video/file/route.ts",
          message: "backend file fetch not ok",
          data: { jobId, status: res.status, detail: detail.slice(0, 120) },
          timestamp: Date.now(),
          hypothesisId: "H7",
          runId: "post-fix-2",
        }),
      }).catch(() => {});
      // #endregion
      return new Response(detail || "Video not found", { status: res.status });
    }

    const buffer = await res.arrayBuffer();
    // #region agent log
    fetch("http://127.0.0.1:7574/ingest/3c6afa58-30ac-4e5e-9854-7a3b8425de96", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Debug-Session-Id": "ba63c3",
      },
      body: JSON.stringify({
        sessionId: "ba63c3",
        location: "api/lesson-video/file/route.ts",
        message: "serving lesson mp4",
        data: { jobId, bytes: buffer.byteLength },
        timestamp: Date.now(),
        hypothesisId: "H7",
        runId: "post-fix-2",
      }),
    }).catch(() => {});
    // #endregion

    return new Response(buffer, {
      status: 200,
      headers: {
        "Content-Type": res.headers.get("Content-Type") ?? "video/mp4",
        "Content-Length": String(buffer.byteLength),
        "Cache-Control": "private, max-age=3600",
        "Accept-Ranges": "bytes",
      },
    });
  } catch {
    return new Response("Cannot reach API server", { status: 503 });
  }
}
