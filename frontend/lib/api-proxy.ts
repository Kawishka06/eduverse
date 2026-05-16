/** Server-side proxy to FastAPI — used by Next.js route handlers only. */

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function backendUrl(path: string): string {
  const base = BACKEND_URL.replace(/\/$/, "");
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base}${p}`;
}

export async function proxyJson(
  path: string,
  request: Request,
  init?: RequestInit,
): Promise<Response> {
  const auth = request.headers.get("authorization");
  const headers: HeadersInit = {
    ...(init?.headers as Record<string, string>),
  };
  if (auth) headers.Authorization = auth;

  let res: Response;
  try {
    res = await fetch(backendUrl(path), {
      ...init,
      headers,
    });
  } catch {
    return Response.json(
      {
        detail:
          "Cannot reach the API server. Start the backend: cd backend && uvicorn main:app --reload",
      },
      { status: 503 },
    );
  }

  const text = await res.text();
  return new Response(text, {
    status: res.status,
    headers: { "Content-Type": res.headers.get("content-type") ?? "application/json" },
  });
}
