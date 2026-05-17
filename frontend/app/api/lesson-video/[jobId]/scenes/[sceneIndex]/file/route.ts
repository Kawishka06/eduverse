import { backendUrl } from "@/lib/api-proxy";
import { getServerAccessToken } from "@/lib/supabase/server-auth";

type RouteContext = { params: Promise<{ jobId: string; sceneIndex: string }> };

export const maxDuration = 120;

export async function GET(request: Request, context: RouteContext) {
  const { jobId, sceneIndex } = await context.params;
  const authHeader = request.headers.get("authorization");
  const token =
    authHeader?.replace(/^Bearer\s+/i, "").trim() || (await getServerAccessToken());

  if (!token) {
    return new Response("Sign in required", { status: 401 });
  }

  try {
    const res = await fetch(
      backendUrl(`/ai/lesson-video/${jobId}/scenes/${sceneIndex}/file`),
      { headers: { Authorization: `Bearer ${token}` } },
    );
    if (!res.ok) {
      return new Response(await res.text(), { status: res.status });
    }
    const buffer = await res.arrayBuffer();
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
