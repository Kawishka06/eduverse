"""Parse fal.ai JSON payloads into normalized values."""

from __future__ import annotations

from typing import Any

from app.services.fal.exceptions import FalResponseParseError


def parse_image_url(data: dict[str, Any]) -> str:
    images = data.get("images")
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
        if isinstance(first, str):
            return first

    image = data.get("image")
    if isinstance(image, dict) and image.get("url"):
        return image["url"]
    if isinstance(image, str):
        return image

    raise FalResponseParseError("No image URL in fal.ai response")


def parse_video_url(data: dict[str, Any]) -> str:
    video = data.get("video")
    if isinstance(video, dict) and video.get("url"):
        return video["url"]
    if isinstance(video, str):
        return video

    videos = data.get("videos")
    if isinstance(videos, list) and videos:
        first = videos[0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
        if isinstance(first, str):
            return first

    output = data.get("output")
    if isinstance(output, dict) and output.get("url"):
        return output["url"]

    raise FalResponseParseError("No video URL in fal.ai response")


def parse_text_output(data: dict[str, Any]) -> str:
    for key in ("text", "caption", "description", "output", "result"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    results = data.get("results")
    if isinstance(results, str) and results.strip():
        return results.strip()

    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, str):
            return first.strip()
        if isinstance(first, dict):
            for key in ("text", "caption", "description"):
                if isinstance(first.get(key), str) and first[key].strip():
                    return first[key].strip()

    raise FalResponseParseError("No text output in fal.ai response")


def parse_audio_url(data: dict[str, Any]) -> str:
    audio = data.get("audio")
    if isinstance(audio, dict) and audio.get("url"):
        return audio["url"]
    if isinstance(audio, str):
        return audio

    for key in ("audio_url", "url"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    raise FalResponseParseError("No audio URL in fal.ai response")
