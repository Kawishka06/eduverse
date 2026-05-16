import { createClient } from "@/lib/supabase/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type TutorMode = "standard" | "simple" | "meme";

type TutorRequestBody = {
  question: string;
  mode: TutorMode;
  character_id?: string | null;
};

type AgentStep = {
  step_type: string;
  tool_name?: string | null;
  input?: Record<string, unknown> | null;
  output?: string | null;
};

type AgentBackendResponse = {
  answer: string;
  message: string;
  model: string;
  mode: string;
  steps: AgentStep[];
};

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function POST(request: Request) {
<<<<<<< HEAD
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return Response.json({ detail: "Sign in to use the tutor." }, { status: 401 });
  }

  const {
    data: { session },
  } = await supabase.auth.getSession();

=======
  const auth = request.headers.get("authorization");
  if (!auth) {
    return Response.json({ detail: "Sign in to use the AI tutor." }, { status: 401 });
  }

>>>>>>> 140e298 (Save local progress)
  let body: TutorRequestBody;
  try {
    body = await request.json();
  } catch {
    return Response.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  if (!body.question?.trim()) {
    return Response.json({ detail: "Question is required" }, { status: 400 });
  }

<<<<<<< HEAD
  const backendRes = await fetch(`${BACKEND_URL}/ai/tutor`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session?.access_token ?? ""}`,
=======
  const backendRes = await fetch(`${BACKEND_URL}/ai/agent/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: auth,
>>>>>>> 140e298 (Save local progress)
    },
    body: JSON.stringify({
      message: body.question.trim(),
      mode: body.mode ?? "standard",
      character_id: body.character_id ?? null,
      material_ids: [],
    }),
  });

  if (!backendRes.ok) {
    const err = await backendRes.json().catch(() => ({}));
    return Response.json(
      { detail: err.detail ?? "Tutor request failed" },
      { status: backendRes.status },
    );
  }

  const data = (await backendRes.json()) as AgentBackendResponse;
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      for (const step of data.steps ?? []) {
        controller.enqueue(
          encoder.encode(`${JSON.stringify({ type: "step", step })}\n`),
        );
        await sleep(40);
      }

      const tokens = data.answer.split(/(\s+)/);
      for (const token of tokens) {
        controller.enqueue(
          encoder.encode(`${JSON.stringify({ type: "delta", content: token })}\n`),
        );
        await sleep(token.trim() ? 28 : 8);
      }

      controller.enqueue(
        encoder.encode(
          `${JSON.stringify({
            type: "done",
            mode: data.mode,
            model: data.model,
            steps: data.steps,
          })}\n`,
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
