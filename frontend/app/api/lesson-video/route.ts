import { proxyJson } from "@/lib/api-proxy";

export async function POST(request: Request) {
  const body = await request.text();
  return proxyJson("/ai/lesson-video", request, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
}

export const maxDuration = 60;
