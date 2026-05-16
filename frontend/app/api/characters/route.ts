import { proxyJson } from "@/lib/api-proxy";

export async function GET(request: Request) {
  return proxyJson("/characters", request);
}

export async function POST(request: Request) {
  const body = await request.text();
  return proxyJson("/characters", request, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
}

export const maxDuration = 300;
