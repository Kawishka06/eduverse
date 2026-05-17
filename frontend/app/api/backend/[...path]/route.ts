import { backendUrl } from "@/lib/api-proxy";
import { getServerAccessToken } from "@/lib/supabase/server-auth";

type RouteContext = { params: Promise<{ path: string[] }> };

async function proxy(request: Request, context: RouteContext): Promise<Response> {
  const { path } = await context.params;
  const targetPath = path.join("/");
  const search = new URL(request.url).search;
  const target = backendUrl(`/${targetPath}${search}`);

  const authHeader = request.headers.get("authorization");
  const token =
    authHeader?.replace(/^Bearer\s+/i, "").trim() || (await getServerAccessToken());

  const headers = new Headers();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("Content-Type", contentType);
  }

  const init: RequestInit = {
    method: request.method,
    headers,
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }

  try {
    const res = await fetch(target, init);
    const outHeaders = new Headers();
    const resType = res.headers.get("content-type");
    if (resType) outHeaders.set("Content-Type", resType);
    const length = res.headers.get("content-length");
    if (length) outHeaders.set("Content-Length", length);

    return new Response(await res.arrayBuffer(), {
      status: res.status,
      headers: outHeaders,
    });
  } catch {
    return Response.json(
      {
        detail:
          "Cannot reach the API server. Deploy the FastAPI backend and set API_URL on Vercel.",
      },
      { status: 503 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;

export const maxDuration = 120;
