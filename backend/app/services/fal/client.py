"""Low-level fal.ai client with live API calls and mock fallbacks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.config import Settings
from app.services.ai.helpers.fal import configure_fal_key, run_fal_model
from app.services.fal import mocks
from app.services.fal.exceptions import FalRequestError
from app.services.fal.models import FalRawResponse


class BaseFalClient(ABC):
    @abstractmethod
    async def invoke(self, model: str, arguments: dict[str, Any]) -> FalRawResponse:
        pass


class MockFalClient(BaseFalClient):
    """Returns deterministic placeholder payloads without calling fal.ai."""

    _HANDLERS = {
        "image": mocks.mock_image_payload,
        "video": mocks.mock_video_payload,
        "vision": mocks.mock_image_to_text_payload,
        "tts": mocks.mock_text_to_speech_payload,
    }

    def __init__(self, operation: str):
        self.operation = operation

    async def invoke(self, model: str, arguments: dict[str, Any]) -> FalRawResponse:
        handler = self._HANDLERS[self.operation]

        if self.operation == "image":
            data = handler(arguments["prompt"], model)
        elif self.operation == "video":
            data = handler(arguments["image_url"], model)
        elif self.operation == "vision":
            data = handler(arguments["image_url"], model)
        elif self.operation == "tts":
            data = handler(arguments["text"], model)
        else:
            data = {"mock": True, "model": model}

        return FalRawResponse(data=data, model=model, mock=True)


class LiveFalClient(BaseFalClient):
    """Executes real fal.ai model calls via fal-client."""

    def __init__(self, settings: Settings):
        self.settings = settings
        configure_fal_key(settings.fal_key)

    async def invoke(self, model: str, arguments: dict[str, Any]) -> FalRawResponse:
        try:
            data = await run_fal_model(
                model,
                arguments,
                timeout=self.settings.fal_request_timeout,
            )
        except Exception as exc:
            raise FalRequestError(f"fal.ai call failed for '{model}': {exc}") from exc

        return FalRawResponse(data=data, model=model, mock=False)
