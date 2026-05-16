"""Extract text from uploaded study materials."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

from app.services.ai.exceptions import FalAPIError
from app.services.ai.helpers.fal import run_fal_model
from app.services.fal import parsers

if TYPE_CHECKING:
    from app.config import Settings


async def extract_text_from_bytes(
    data: bytes,
    content_type: str,
    *,
    settings: Settings,
    file_url: str | None = None,
) -> str:
    ct = (content_type or "").lower()

    if ct.startswith("text/") or ct in ("application/json", "application/xml"):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")

    if ct in ("application/octet-stream", "binary/octet-stream") and data:
        # Last resort: try UTF-8 for files saved as generic binary
        try:
            text = data.decode("utf-8")
            if text.strip() and "\x00" not in text[:1024]:
                return text
        except UnicodeDecodeError:
            pass

    if ct == "application/pdf":
        return _extract_pdf(data)

    if ct.startswith("image/"):
        if not file_url:
            raise ValueError("Image ingestion requires a public file URL")
        return await _caption_image(file_url, settings)

    return ""


def _extract_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required for PDF ingestion") from exc

    reader = PdfReader(io.BytesIO(data))
    parts: list[str] = []
    for page in reader.pages[:40]:
        text = page.extract_text()
        if text:
            parts.append(text.strip())
    return "\n\n".join(parts)


async def _caption_image(image_url: str, settings: Settings) -> str:
    if settings.fal_mock_mode or not settings.fal_key:
        return f"[MOCK caption for image at {image_url}]"

    result = await run_fal_model(
        settings.fal_vision_model,
        {"image_url": image_url},
        timeout=settings.fal_request_timeout,
    )
    try:
        return parsers.parse_text_output(result)
    except Exception as exc:
        raise FalAPIError(f"Vision caption failed: {exc}") from exc
