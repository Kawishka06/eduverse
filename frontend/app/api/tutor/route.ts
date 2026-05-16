const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type TutorMode = "standard" | "simple" | "meme";

type TutorRequestBody = {
  question: string;
  context?: string;
  mode: TutorMode;
};

type TutorBackendResponse = {
  answer: string;
  question: string;
  model: string;
  mode: string;
};

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function POST(request: Request) {
  let body: TutorRequestBody;
  try {
    body = await request.json();
  } catch {
    return Response.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  if (!body.question?.trim()) {
    return Response.json({ detail: "Question is required" }, { status: 400 });
  }

  const auth = request.headers.get("authorization");

  const backendRes = await fetch(`${BACKEND_URL}/ai/tutor`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(auth ? { Authorization: auth } : {}),
    },
    body: JSON.stringify({
      question: body.question.trim(),
      context: body.context?.trim() || null,
      mode: body.mode ?? "standard",
    }),
  });

  if (!backendRes.ok) {
    const err = await backendRes.json().catch(() => ({}));
    return Response.json(
      { detail: err.detail ?? "Tutor request failed" },
      { status: backendRes.status },
    );
  }

  const data = (await backendRes.json()) as TutorBackendResponse;
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const tokens = data.answer.split(/(\s+)/);

      for (const token of tokens) {
        controller.enqueue(
          encoder.encode(`${JSON.stringify({ type: "delta", content: token })}\n`),
        );
        await sleep(token.trim() ? 28 : 8);
      }

      controller.enqueue(
        encoder.encode(
          `${JSON.stringify({ type: "done", mode: data.mode, model: data.model })}\n`,
        ),
      );
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "application/x-ndjson",
      "Cache-Control": "no-cache",
    },
  });
}
