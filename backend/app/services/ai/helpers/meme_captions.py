"""Meme top/bottom captions — LLM when available, free templates otherwise."""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass

from app.config import Settings, get_settings
from app.services.ai.helpers.llm import ask_llm

MEME_CAPTION_SYSTEM = """You write classic internet meme captions in English.
Return ONLY valid JSON with this exact shape:
{"top_text": "SHORT TOP LINE", "bottom_text": "SHORT BOTTOM LINE"}

Rules:
- ALL CAPS
- Max 12 words per line (short and readable on a meme)
- Funny, relatable to the topic
- Proper English spelling; keep apostrophes in contractions (DON'T, WE'RE)
- No quotes inside the text
- No explanation outside the JSON"""

_TOP_LINE_RE = re.compile(r"^top\s*text\s*:\s*(.+)$", re.IGNORECASE)
_BOTTOM_LINE_RE = re.compile(r"^bottom\s*text\s*:\s*(.+)$", re.IGNORECASE)
_INSTRUCTION_LINE_RE = re.compile(
    r"^(create|make|add|use|show|turn|write|return|rules?|topic)\b",
    re.IGNORECASE,
)


@dataclass
class ParsedMemePrompt:
    scene_description: str
    explicit_top: str | None = None
    explicit_bottom: str | None = None


def _strip_quotes(value: str) -> str:
    return value.strip().strip("\"'“”").strip()


def parse_meme_user_prompt(text: str) -> ParsedMemePrompt:
    """Split user prompt into scene (for image) and optional overlay lines."""
    explicit_top: str | None = None
    explicit_bottom: str | None = None
    scene_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        top_m = _TOP_LINE_RE.match(stripped)
        if top_m:
            explicit_top = _strip_quotes(top_m.group(1))
            continue
        bottom_m = _BOTTOM_LINE_RE.match(stripped)
        if bottom_m:
            explicit_bottom = _strip_quotes(bottom_m.group(1))
            continue
        scene_lines.append(stripped)

    scene = _extract_scene_description("\n".join(scene_lines))
    return ParsedMemePrompt(
        scene_description=scene,
        explicit_top=explicit_top,
        explicit_bottom=explicit_bottom,
    )


def _extract_scene_description(text: str) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    if not t:
        return "funny relatable student study moment"

    about = re.search(
        r"(?:about|showing|depicting)\s+(.+?)(?:\.|make it|use a|add short|$)",
        t,
        re.IGNORECASE,
    )
    if about:
        return about.group(1).strip()[:220]

    setting = re.search(
        r"(classroom|study\s+table|library|dorm|lecture\s+hall|exam\s+prep)[^.]{0,120}",
        t,
        re.IGNORECASE,
    )
    if setting:
        return setting.group(0).strip()[:220]

    parts: list[str] = []
    for sentence in re.split(r"[.!?]\s+", t):
        s = sentence.strip()
        if not s or len(s) < 12:
            continue
        if _INSTRUCTION_LINE_RE.match(s):
            continue
        if re.search(r"\b(top|bottom)\s*text\b", s, re.IGNORECASE):
            continue
        parts.append(s)
        if len(" ".join(parts)) > 180:
            break

    if parts:
        return " ".join(parts)[:220]

    return t[:220]


def _normalize_caption(line: str, max_words: int = 12) -> str:
    cleaned = re.sub(r"\s+", " ", line.strip().upper())
    cleaned = re.sub(r"[^A-Z0-9\s'!?.,:;\-]", "", cleaned)
    words = cleaned.split()[:max_words]
    return " ".join(words) if words else "MEME TIME"


def _format_user_overlay_line(line: str) -> str:
    """Preserve user-provided meme lines with readable length."""
    return _normalize_caption(line, max_words=14)


def free_meme_captions(topic: str) -> dict[str, str]:
    """Rule-based captions — no API cost."""
    t = topic.lower()

    if "html" in t and ("debug" in t or "fix" in t or "error" in t):
        return {
            "top_text": "WHEN YOU FORGET TO CLOSE A DIV",
            "bottom_text": "AND THE WHOLE PAGE BREAKS",
        }
    if "html" in t or "css" in t:
        return {
            "top_text": "ME TRYING TO CENTER A DIV",
            "bottom_text": "WITH PURE HTML AND CSS",
        }
    if "python" in t:
        return {
            "top_text": "IT WORKS ON MY MACHINE",
            "bottom_text": "MUST BE A YOU PROBLEM",
        }
    if "javascript" in t or "js" in t:
        return {
            "top_text": "undefined IS NOT A FUNCTION",
            "bottom_text": "I AM NOT A FUNCTION",
        }
    if ("last minute" in t or "night before" in t) and ("exam" in t or "test" in t):
        return {
            "top_text": "ME OPENING THE TEXTBOOK ONE NIGHT BEFORE EXAM",
            "bottom_text": "BRAIN: WE DON'T DO THAT HERE",
        }
    if "exam" in t or "test" in t or "study" in t:
        return {
            "top_text": "WHEN THE EXAM IS TOMORROW",
            "bottom_text": "AND YOU JUST STARTED STUDYING",
        }
    if "bug" in t or "debug" in t:
        return {
            "top_text": "FOUND THE BUG IN PRODUCTION",
            "bottom_text": "IT WAS A TYPO ALL ALONG",
        }

    short = _normalize_caption(topic, max_words=5)
    return {
        "top_text": f"WHEN YOU LEARN ABOUT {short}",
        "bottom_text": "AND IT FINALLY CLICKS",
    }


def _parse_caption_json(raw: str) -> dict[str, str] | None:
    text = raw.strip()
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return None

    top = data.get("top_text") or data.get("top")
    bottom = data.get("bottom_text") or data.get("bottom")
    if not top or not bottom:
        return None

    return {
        "top_text": _normalize_caption(str(top)),
        "bottom_text": _normalize_caption(str(bottom)),
    }


async def generate_meme_captions(
    topic: str,
    settings: Settings | None = None,
    *,
    parsed: ParsedMemePrompt | None = None,
) -> dict[str, str]:
    settings = settings or get_settings()
    topic = topic.strip()
    prompt_parts = parsed or parse_meme_user_prompt(topic)

    if prompt_parts.explicit_top and prompt_parts.explicit_bottom:
        return {
            "top_text": _format_user_overlay_line(prompt_parts.explicit_top),
            "bottom_text": _format_user_overlay_line(prompt_parts.explicit_bottom),
        }

    scene = prompt_parts.scene_description or topic

    if settings.fal_mock_mode or not settings.fal_key:
        return free_meme_captions(scene)

    try:
        raw = await ask_llm(
            f"Scene / topic for the meme (write captions only, no image): {scene}",
            None,
            model=settings.fal_llm_model,
            endpoint=settings.fal_llm_endpoint,
            max_tokens=160,
            timeout=settings.fal_request_timeout,
            system_prompt=MEME_CAPTION_SYSTEM,
        )
        caption_json = _parse_caption_json(raw)
        if caption_json:
            return caption_json
    except Exception:
        pass

    return free_meme_captions(scene)


FEED_CAPTION_TEMPLATES = [
    "This one broke my brain today 🤯",
    "Tag someone who needs to see this",
    "Study mood in one picture",
    "When the lecture finally makes sense",
    "Me explaining this to my group chat",
    "Certified EduVerse moment",
    "No thoughts just vibes (and bugs)",
    "POV: you opened the assignment at midnight",
    "Sending this to the study group",
    "Why is this so accurate though",
    "Another day in the learning trenches",
    "I felt this in my soul",
    "The algorithm knew I needed this",
    "Saving this for exam season",
    "Can't stop thinking about this topic",
]


def _overlay_signature(top: str, bottom: str) -> str:
    return f"{top.strip().upper()}|{bottom.strip().upper()}"


def generate_feed_caption(topic: str, top_text: str, bottom_text: str) -> str:
    """Social feed caption — always different from meme overlay lines."""
    topic = topic.strip() or "this topic"
    overlay_sig = _overlay_signature(top_text, bottom_text)
    overlay_joined = " / ".join(
        x for x in (top_text.strip(), bottom_text.strip()) if x
    ).upper()

    candidates = list(FEED_CAPTION_TEMPLATES)
    random.shuffle(candidates)

    for pick in candidates:
        if _overlay_signature(pick, "") != overlay_sig and pick.upper() != overlay_joined:
            return pick[:200]

    return f"Learning about {topic[:50]} — what do you think?"[:200]


def build_meme_post_caption(feed_caption: str, top_text: str, bottom_text: str) -> str:
    """JSON stored in posts.caption: overlay text + separate feed caption."""
    return json.dumps(
        {
            "kind": "meme",
            "feed": feed_caption,
            "top": top_text,
            "bottom": bottom_text,
        },
        ensure_ascii=False,
    )
