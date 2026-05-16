import { proxyJson } from "@/lib/api-proxy";

type Params = { params: Promise<{ id: string }> };

export async function DELETE(request: Request, { params }: Params) {
  const { id } = await params;
  return proxyJson(`/content/materials/${id}`, request, { method: "DELETE" });
}
