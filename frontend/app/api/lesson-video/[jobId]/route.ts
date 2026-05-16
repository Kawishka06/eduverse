import { proxyJson } from "@/lib/api-proxy";

type Params = { params: Promise<{ jobId: string }> };

export async function GET(request: Request, { params }: Params) {
  const { jobId } = await params;
  return proxyJson(`/ai/lesson-video/${jobId}`, request);
}
