const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type MemeGenerateResponse = {
  image_url: string;
  prompt: string;
  model: string;
};

export async function generateMeme(
  text: string,
  token?: string | null,
): Promise<MemeGenerateResponse> {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/ai/meme`, {
    method: "POST",
    headers,
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail =
      typeof body.detail === "string"
        ? body.detail
        : "Failed to generate meme. Please try again.";
    throw new Error(detail);
  }

  return res.json();
}
