"""Abstracted async helpers for fal.ai model calls."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import fal_client

from app.services.ai.exceptions import FalAPIError

_REMOTE_IMAGE_PREFIXES = ("http://", "https://", "data:")


def configure_fal_key(api_key: str | None) -> None:
    if api_key:
        os.environ["FAL_KEY"] = api_key


async def run_fal_model(
    application: str,
    arguments: dict[str, Any],
    *,
    timeout: float | None = None,
) -> dict[str, Any]:
    """Run a fal.ai model and return the parsed JSON response."""
    try:
        result = await fal_client.run_async(
            application,
            arguments,
            timeout=timeout,
        )
    except Exception as exc:
        raise FalAPIError(f"fal.ai request failed for '{application}': {exc}") from exc

    if not isinstance(result, dict):
        raise FalAPIError(f"Unexpected fal.ai response type: {type(result).__name__}")

    return result


async def text_to_image(
    prompt: str,
    *,
    model: str,
    image_size: str = "square_hd",
    num_images: int = 1,
    timeout: float | None = None,
    **extra_args: Any,
) -> dict[str, Any]:
    """Text → image via a fal.ai diffusion model."""
    arguments: dict[str, Any] = {
        "prompt": prompt,
        "image_size": image_size,
        "num_images": num_images,
        **extra_args,
    }
    return await run_fal_model(model, arguments, timeout=timeout)


async def image_to_video(
    image_url: str,
    *,
    model: str,
    prompt: str | None = None,
    timeout: float | None = None,
    **extra_args: Any,
) -> dict[str, Any]:
    """Image → video via a fal.ai video model."""
    arguments: dict[str, Any] = {"image_url": image_url, **extra_args}
    if prompt:
        arguments["prompt"] = prompt
    return await run_fal_model(model, arguments, timeout=timeout)


async def resolve_image_input(image: str) -> str:
    """
    Normalize image input for fal.ai.

    Accepts HTTP(S) URLs, data URIs, or local file paths (uploaded via fal).
    """
    if image.startswith(_REMOTE_IMAGE_PREFIXES):
        return image

    path = Path(image)
    if not path.is_file():
        raise FalAPIError(f"Image not found and not a valid URL: {image}")

    try:
        return fal_client.encode_file(str(path))
    except Exception as exc:
        raise FalAPIError(f"Failed to encode image file '{image}': {exc}") from exc


def extract_image_url(result: dict[str, Any]) -> str:
    images = result.get("images")
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
        if isinstance(first, str):
            return first

    image = result.get("image")
    if isinstance(image, dict) and image.get("url"):
        return image["url"]
    if isinstance(image, str):
        return image

    raise FalAPIError("No image URL found in fal.ai response")


def extract_video_url(result: dict[str, Any]) -> str:
    video = result.get("video")
    if isinstance(video, dict) and video.get("url"):
        return video["url"]
    if isinstance(video, str):
        return video

    videos = result.get("videos")
    if isinstance(videos, list) and videos:
        first = videos[0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
        if isinstance(first, str):
            return first

    output = result.get("output")
    if isinstance(output, dict) and output.get("url"):
        return output["url"]

    raise FalAPIError("No video URL found in fal.ai response")
