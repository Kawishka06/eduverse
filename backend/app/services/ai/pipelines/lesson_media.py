"""Download fal assets and mux silent video + TTS into one MP4 (requires ffmpeg)."""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
from pathlib import Path

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


def ffmpeg_executable() -> str | None:
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def ffmpeg_available() -> bool:
    return ffmpeg_executable() is not None


def scene_render_path(settings: Settings, job_id: str, scene_index: int) -> Path:
    root = settings.lesson_data_dir / "renders" / job_id
    root.mkdir(parents=True, exist_ok=True)
    return root / f"scene_{scene_index}.mp4"


def scene_render_url(settings: Settings, job_id: str, scene_index: int) -> str:
    base = settings.api_public_url.rstrip("/")
    return f"{base}/ai/lesson-video/{job_id}/scenes/{scene_index}/file"


async def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        dest.write_bytes(resp.content)


def _mux_files(video_path: Path, audio_path: Path, output_path: Path) -> None:
    ffmpeg = ffmpeg_executable()
    if not ffmpeg:
        raise RuntimeError("ffmpeg not available")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "ffmpeg failed")[:400])


async def build_scene_video_with_voice(
    *,
    job_id: str,
    scene_index: int,
    video_url: str,
    audio_url: str,
    settings: Settings,
) -> str | None:
    """
    Merge fal silent clip + narration audio into one file.
    Returns public URL to the muxed MP4, or None if ffmpeg missing / failure.
    """
    if not ffmpeg_available():
        logger.warning("ffmpeg not found — cannot mux voice into video")
        return None

    work = settings.lesson_data_dir / "renders" / job_id / f"_work_{scene_index}"
    work.mkdir(parents=True, exist_ok=True)
    v_in = work / "clip.mp4"
    a_in = work / "narration.mp3"
    out = scene_render_path(settings, job_id, scene_index)

    try:
        await _download(video_url, v_in)
        await _download(audio_url, a_in)
        await asyncio.to_thread(_mux_files, v_in, a_in, out)
        return scene_render_url(settings, job_id, scene_index)
    except Exception as exc:
        logger.warning("Mux scene %s job %s failed: %s", scene_index, job_id, exc)
        return None
    finally:
        for p in (v_in, a_in):
            try:
                p.unlink(missing_ok=True)
            except OSError:
                pass
