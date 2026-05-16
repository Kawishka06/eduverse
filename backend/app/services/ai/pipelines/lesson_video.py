"""Lesson video pipeline: script → scene images → TTS → image-to-video."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

from app.config import Settings
from app.services.ai.exceptions import AIOrchestratorError
from app.services.ai.helpers.fal import (
    extract_image_url,
    extract_video_url,
    image_to_video,
    run_fal_model,
    text_to_image,
)
from app.services.ai.helpers.llm import _extract_llm_text
from app.services.ai.pipelines.lesson_media import (
    build_scene_video_with_voice,
    ffmpeg_available,
    scene_render_path,
)
from app.services.ai.pipelines.lesson_video_jobs import LessonVideoJobRepository
from app.services.fal import parsers
from app.services.fal.mocks import MOCK_AUDIO_URL

# MiniMax Speech-02 HD voice presets (fal-ai/minimax/speech-02-hd)
VOICE_STYLE_TO_MINIMAX: dict[str, str] = {
    "friendly": "Wise_Woman",
    "warm": "Calm_Woman",
    "calm": "Calm_Woman",
    "energetic": "Lively_Girl",
    "professional": "Deep_Voice_Man",
    "deep": "Deep_Voice_Man",
    "childlike": "Cute_Girl",
}

# Kokoro (legacy; set FAL_TTS_MODEL=fal-ai/kokoro/american-english to use)
VOICE_STYLE_TO_KOKORO: dict[str, str] = {
    "friendly": "af_bella",
    "warm": "af_heart",
    "calm": "af_sarah",
    "energetic": "af_nova",
    "professional": "am_michael",
    "deep": "am_adam",
    "childlike": "af_sky",
}


def _minimax_voice(voice_style: str) -> str:
    key = (voice_style or "friendly").strip().lower()
    return VOICE_STYLE_TO_MINIMAX.get(key, "Wise_Woman")


def _kokoro_voice(voice_style: str) -> str:
    key = (voice_style or "friendly").strip().lower()
    return VOICE_STYLE_TO_KOKORO.get(key, "af_bella")


def _tts_payload(text: str, voice_style: str, model: str) -> dict[str, Any]:
    snippet = text.strip()[:500]
    if "kokoro" in model:
        return {"text": snippet, "voice": _kokoro_voice(voice_style)}
    return {
        "text": snippet,
        "voice_setting": {"voice_id": _minimax_voice(voice_style)},
        "output_format": "url",
    }


SCRIPT_SYSTEM = """You are an educational video scriptwriter.
From the study material, create a short lesson with 3 to 5 scenes.
Each scene narration must teach real facts from the material (the character will read it aloud).

Create exactly 3 scenes (not more).

Return ONLY valid JSON:
{
  "title": "Lesson title",
  "scenes": [
    {
      "title": "Scene name",
      "narration": "What the character says aloud (2-4 sentences, factual, from the material)",
      "visual_prompt": "Detailed scene description for image generation",
      "on_screen_text": "Short keyword or phrase on screen"
    }
  ]
}
No markdown, no code fences."""


async def generate_lesson_script(material_text: str, settings: Settings) -> dict[str, Any]:
    if settings.fal_mock_mode or not settings.fal_key:
        return _mock_script(material_text)

    snippet = material_text[:8000]
    result = await run_fal_model(
        settings.fal_llm_endpoint,
        {
            "model": settings.fal_llm_model,
            "prompt": f"Study material:\n{snippet}\n\nCreate the lesson JSON.",
            "system_prompt": SCRIPT_SYSTEM,
            "max_tokens": 2048,
        },
        timeout=settings.fal_request_timeout,
    )
    raw = _extract_llm_text(result)
    parsed = _extract_json(raw)
    if parsed and parsed.get("scenes"):
        return parsed
    return _mock_script(material_text)


def _mock_script(material_text: str) -> dict[str, Any]:
    topic = material_text[:80].strip() or "Your lesson"
    return {
        "title": f"Lesson: {topic[:50]}",
        "scenes": [
            {
                "title": "Introduction",
                "narration": f"Welcome! Today we explore {topic[:60]}.",
                "visual_prompt": "Friendly cartoon teacher in a bright classroom, welcoming gesture",
                "on_screen_text": "Intro",
            },
            {
                "title": "Main idea",
                "narration": "Here is the core concept from your notes, broken into simple steps.",
                "visual_prompt": "Educational diagram style illustration, colorful, student-friendly",
                "on_screen_text": "Key idea",
            },
            {
                "title": "Summary",
                "narration": "Great job! Review these points and teach a friend what you learned.",
                "visual_prompt": "Celebration scene with books and lightbulb, positive mood",
                "on_screen_text": "Recap",
            },
        ],
    }


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None
    return None


async def _synthesize_narration(
    narration: str,
    *,
    settings: Settings,
    voice_style: str,
) -> str | None:
    narration = narration.strip()
    if not narration:
        return None

    if settings.fal_mock_mode or not settings.fal_key:
        return MOCK_AUDIO_URL

    payload = _tts_payload(narration, voice_style, settings.fal_tts_model)
    tts_raw = await run_fal_model(
        settings.fal_tts_model,
        payload,
        timeout=settings.fal_request_timeout,
    )
    return parsers.parse_audio_url(tts_raw)


async def run_lesson_video_job(
    job_id: str,
    *,
    material_text: str,
    character_bible: str,
    reference_image_url: str | None,
    voice_style: str = "friendly",
    settings: Settings,
) -> None:
    repo = LessonVideoJobRepository()

    def _phase(message: str, progress: int, **extra: Any) -> None:
        repo.update(
            job_id,
            {
                "status": "processing",
                "progress": progress,
                "phase": message,
                **extra,
            },
        )

    try:
        _phase("Writing lesson script from your notes…", 5)

        script = await generate_lesson_script(material_text, settings)
        title = str(script.get("title", "Lesson"))
        scenes_in = script.get("scenes") or []
        scenes_out: list[dict[str, Any]] = []

        _phase(f"Script ready: {title}", 10, title=title)

        total = max(len(scenes_in), 1)
        for idx, scene in enumerate(scenes_in):
            scene_num = idx + 1
            slice_size = 80 // total
            base_progress = 10 + idx * slice_size
            _phase(f"Scene {scene_num}/{total}: generating visuals…", base_progress)

            visual = str(scene.get("visual_prompt", ""))
            char_lock = f"Character: {character_bible[:400]}. " if character_bible else ""
            ref_note = " Match the reference character design exactly." if reference_image_url else ""
            image_prompt = (
                f"{char_lock}{visual}{ref_note} "
                "Educational illustration, vibrant, student-friendly, no text in image. "
                "Single clear composition suitable for subtle animation."
            )
            motion_prompt = (
                f"Gentle educational motion: {visual[:180]}. "
                "Slow camera push, soft lighting, living scene, no text."
            )

            image_url: str | None = None
            audio_url: str | None = None
            video_url: str | None = None

            narration = str(scene.get("narration", ""))

            if settings.fal_mock_mode or not settings.fal_key:
                image_url = "https://placehold.co/1024x576/png?text=Scene"
                audio_url = await _synthesize_narration(
                    narration, settings=settings, voice_style=voice_style
                )
                video_url = None
            else:
                extra: dict[str, Any] = {}
                if reference_image_url:
                    extra["image_url"] = reference_image_url

                raw_img = await text_to_image(
                    image_prompt,
                    model=settings.fal_character_model,
                    image_size="landscape_16_9",
                    num_images=1,
                    timeout=settings.fal_request_timeout,
                    **extra,
                )
                image_url = extract_image_url(raw_img)

                _phase(
                    f"Scene {scene_num}/{total}: recording character voice…",
                    base_progress + slice_size // 3,
                )
                audio_url = await _synthesize_narration(
                    narration, settings=settings, voice_style=voice_style
                )

            scene_record = {
                "title": str(scene.get("title", f"Scene {idx + 1}")),
                "narration": str(scene.get("narration", "")),
                "visual_prompt": visual,
                "on_screen_text": str(scene.get("on_screen_text", "")),
                "image_url": image_url,
                "audio_url": audio_url,
                "video_url": None,
            }
            scenes_out.append(scene_record)

            if (
                settings.lesson_enable_video_clips
                and image_url
                and not settings.fal_mock_mode
                and settings.fal_key
            ):
                _phase(
                    f"Scene {scene_num}/{total}: animating video (up to {int(settings.lesson_video_timeout)}s)…",
                    base_progress + slice_size // 2,
                )
                try:
                    vid_raw = await asyncio.wait_for(
                        image_to_video(
                            image_url,
                            model=settings.fal_video_model,
                            prompt=motion_prompt,
                            timeout=settings.lesson_video_timeout,
                        ),
                        timeout=settings.lesson_video_timeout + 30,
                    )
                    silent_video = extract_video_url(vid_raw)
                    scene_record["video_url"] = silent_video

                    if (
                        settings.lesson_mux_voice_into_video
                        and audio_url
                        and ffmpeg_available()
                    ):
                        _phase(
                            f"Scene {scene_num}/{total}: adding character voice to video…",
                            base_progress + (2 * slice_size) // 3,
                        )
                        muxed = await build_scene_video_with_voice(
                            job_id=job_id,
                            scene_index=idx,
                            video_url=silent_video,
                            audio_url=audio_url,
                            settings=settings,
                        )
                        if muxed:
                            scene_record["video_url"] = muxed
                    elif audio_url and not ffmpeg_available():
                        _phase(
                            f"Scene {scene_num}/{total}: install ffmpeg to merge voice into video",
                            base_progress + (2 * slice_size) // 3,
                        )
                except Exception as exc:
                    logger.warning(
                        "Scene %s video failed for job %s: %s",
                        scene_num,
                        job_id,
                        exc,
                    )
                    _phase(
                        f"Scene {scene_num}/{total}: video failed — showing image + voice",
                        base_progress + (2 * slice_size) // 3,
                    )
            else:
                repo.update(
                    job_id,
                    {
                        "scenes_json": list(scenes_out),
                        "progress": 10 + int(((idx + 0.5) / total) * 85),
                    },
                )

            repo.update(
                job_id,
                {
                    "scenes_json": list(scenes_out),
                    "progress": 10 + int(((idx + 1) / total) * 85),
                    "phase": f"Finished scene {scene_num}/{total}",
                },
            )

        playlist = (
            next((s.get("video_url") for s in scenes_out if s.get("video_url")), None)
            or (scenes_out[0].get("audio_url") if scenes_out else None)
        )
        repo.update(
            job_id,
            {
                "status": "completed",
                "progress": 100,
                "title": title,
                "phase": "Done",
                "scenes_json": scenes_out,
                "playlist_url": playlist,
            },
        )
    except Exception as exc:
        repo.update(
            job_id,
            {
                "status": "failed",
                "error_message": str(exc)[:500],
            },
        )
        raise AIOrchestratorError(f"Lesson video job failed: {exc}") from exc
