"""Reusable fal.ai integration service for EduVerse."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.config import Settings, get_settings
from app.services.fal.client import BaseFalClient, LiveFalClient, MockFalClient
from app.services.fal.exceptions import FalServiceError
from app.services.fal.models import (
    ImageGenerationResult,
    ImageToTextResult,
    TextToSpeechResult,
    VideoGenerationResult,
)
from app.services.fal import parsers


class FalService:
    """
    High-level fal.ai service.

    Supports live API calls when FAL_KEY is set, otherwise uses mock responses.
    Force mock mode with FAL_MOCK_MODE=true.
    """

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    @property
    def use_mock(self) -> bool:
        return self.settings.fal_mock_mode or not self.settings.fal_key

    def _client(self, operation: str) -> BaseFalClient:
        if self.use_mock:
            return MockFalClient(operation)
        return LiveFalClient(self.settings)

    async def generate_image(self, prompt: str) -> ImageGenerationResult:
        """Text → image generation."""
        if not prompt.strip():
            raise FalServiceError("Prompt cannot be empty")

        raw = await self._client("image").invoke(
            self.settings.fal_image_model,
            {
                "prompt": prompt.strip(),
                "image_size": "square_hd",
                "num_images": 1,
            },
        )

        return ImageGenerationResult(
            url=parsers.parse_image_url(raw.data),
            prompt=prompt.strip(),
            model=raw.model,
            mock=raw.mock,
        )

    async def generate_video(self, image_url: str) -> VideoGenerationResult:
        """Image URL → video generation."""
        if not image_url.strip():
            raise FalServiceError("image_url cannot be empty")

        raw = await self._client("video").invoke(
            self.settings.fal_video_model,
            {"image_url": image_url.strip()},
        )

        return VideoGenerationResult(
            url=parsers.parse_video_url(raw.data),
            source_image_url=image_url.strip(),
            model=raw.model,
            mock=raw.mock,
        )

    async def image_to_text(self, image_url: str) -> ImageToTextResult:
        """Image URL → caption / description."""
        if not image_url.strip():
            raise FalServiceError("image_url cannot be empty")

        raw = await self._client("vision").invoke(
            self.settings.fal_vision_model,
            {"image_url": image_url.strip()},
        )

        return ImageToTextResult(
            text=parsers.parse_text_output(raw.data),
            image_url=image_url.strip(),
            model=raw.model,
            mock=raw.mock,
        )

    async def text_to_speech(self, text: str) -> TextToSpeechResult:
        """Text → speech audio URL."""
        if not text.strip():
            raise FalServiceError("text cannot be empty")

        raw = await self._client("tts").invoke(
            self.settings.fal_tts_model,
            {"text": text.strip()},
        )

        return TextToSpeechResult(
            audio_url=parsers.parse_audio_url(raw.data),
            text=text.strip(),
            model=raw.model,
            mock=raw.mock,
        )


@lru_cache
def get_fal_service() -> FalService:
    return FalService()
