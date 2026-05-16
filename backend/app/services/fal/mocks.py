"""Placeholder responses when fal.ai is unavailable or mock mode is enabled."""

from __future__ import annotations

import hashlib
from typing import Any

MOCK_IMAGE_BASE = "https://placehold.co/512x512/png"
MOCK_VIDEO_URL = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
MOCK_AUDIO_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"


def _seed(value: str) -> str:
    return hashlib.md5(value.encode(), usedforsecurity=False).hexdigest()[:8]


def mock_image_payload(prompt: str, model: str) -> dict[str, Any]:
    seed = _seed(prompt)
    return {
        "images": [{"url": f"{MOCK_IMAGE_BASE}?text=Mock+Image+{seed}"}],
        "prompt": prompt,
        "model": model,
        "mock": True,
    }


def mock_video_payload(image_url: str, model: str) -> dict[str, Any]:
    return {
        "video": {"url": MOCK_VIDEO_URL},
        "image_url": image_url,
        "model": model,
        "mock": True,
    }


def mock_image_to_text_payload(image_url: str, model: str) -> dict[str, Any]:
    seed = _seed(image_url)
    return {
        "text": (
            f"[MOCK] Image caption for {image_url[:48]}... "
            f"(id: {seed}). Replace with live fal.ai vision model output."
        ),
        "model": model,
        "mock": True,
    }


def mock_text_to_speech_payload(text: str, model: str) -> dict[str, Any]:
    return {
        "audio_url": MOCK_AUDIO_URL,
        "text": text,
        "model": model,
        "mock": True,
    }
