import { backendUrl } from "@/lib/api-proxy";

export async function GET(request: Request) {
  const auth = request.headers.get("authorization");
  try {
    const res = await fetch(backendUrl("/content/materials"), {
      headers: auth ? { Authorization: auth } : {},
    });
    const text = await res.text();
    return new Response(text, {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return Response.json(
      { detail: "Cannot reach the API server. Is the backend running on port 8000?" },
      { status: 503 },
    );
  }
}

export async function POST(request: Request) {
  const auth = request.headers.get("authorization");
  if (!auth) {
    return Response.json({ detail: "Sign in required" }, { status: 401 });
  }

  const form = await request.formData();
  try {
    const res = await fetch(backendUrl("/content/materials"), {
      method: "POST",
      headers: { Authorization: auth },
      body: form,
    });
    const text = await res.text();
    return new Response(text, {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return Response.json(
      { detail: "Cannot reach the API server. Is the backend running on port 8000?" },
      { status: 503 },
    );
  }
}

export const maxDuration = 120;
