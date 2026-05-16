"""LLM helper for the AI tutor."""

from __future__ import annotations

from typing import Any

from app.services.ai.exceptions import LLMError
from app.services.ai.helpers.fal import run_fal_model

TUTOR_SYSTEM_PROMPT = (
    "You are EduVerse AI Tutor, a friendly and concise learning assistant. "
    "Explain concepts clearly, use examples when helpful, and encourage the student. "
    "If context is provided, ground your answer in it."
)

TUTOR_MODE_PROMPTS: dict[str, str] = {
    "standard": TUTOR_SYSTEM_PROMPT,
    "simple": (
        "You are EduVerse AI Tutor. Explain like the student is 10 years old. "
        "Use simple words, short sentences, and everyday analogies. Stay accurate."
    ),
    "meme": (
        "You are EduVerse AI Tutor. Explain the concept using meme culture, witty humor, "
        "and funny analogies (lightly use internet slang). Stay accurate and helpful."
    ),
}


def mock_tutor_answer(question: str, mode: str) -> str:
    if mode == "simple":
        return (
            f"[MOCK · Simple] Think of it like this: {question[:80]}… "
            "Imagine you're explaining it to a friend with easy words and a fun example!"
        )
    if mode == "meme":
        return (
            f"[MOCK · Meme mode] {question[:60]}… "
            "Picture your brain doing a victory dance — that's basically what's happening. "
            "No cap, science is just the universe's DLC pack. 📚✨"
        )
    return (
        f"[MOCK] Here's a clear explanation for: {question[:100]}… "
        "Connect this idea to what you already know and try teaching it back out loud."
    )


async def ask_llm(
    question: str,
    context: str | None,
    *,
    model: str,
    endpoint: str = "fal-ai/any-llm",
    max_tokens: int = 1024,
    timeout: float | None = None,
    system_prompt: str | None = None,
) -> str:
    """Send a tutor question (with optional context) to an LLM via fal.ai."""
    user_prompt = question
    if context:
        user_prompt = f"Context:\n{context.strip()}\n\nQuestion:\n{question.strip()}"

    try:
        result = await run_fal_model(
            endpoint,
            {
                "model": model,
                "prompt": user_prompt,
                "system_prompt": system_prompt or TUTOR_SYSTEM_PROMPT,
                "max_tokens": max_tokens,
            },
            timeout=timeout,
        )
    except Exception as exc:
        raise LLMError(f"Tutor LLM request failed: {exc}") from exc

    answer = _extract_llm_text(result)
    if not answer:
        raise LLMError("LLM returned an empty response")

    return answer


def _extract_llm_text(result: dict[str, Any]) -> str:
    for key in ("output", "text", "response", "content", "answer"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    choices = result.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str) and content.strip():
            return content.strip()

    return ""
