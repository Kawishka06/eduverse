"""HTTPS URL host allowlist for user-supplied media links."""

from __future__ import annotations

from urllib.parse import urlparse

from fastapi import HTTPException, status

from app.config import get_settings


def _allowed_hosts() -> frozenset[str]:
    settings = get_settings()
    hosts = {h.strip().lower() for h in settings.allowed_url_hosts if h.strip()}
    if settings.supabase_url:
        try:
            ref = urlparse(settings.supabase_url).hostname or ""
            if ref:
                hosts.add(ref.lower())
                hosts.add(f"{ref.split('.')[0]}.supabase.co".lower())
        except Exception:
            pass
    return frozenset(hosts)


def _is_lesson_video_file_url(url: str) -> bool:
    """Allow saved lesson MP4 URLs served by our API (dev uses http://localhost)."""
    if "/lesson-video/" not in url or "/file" not in url:
        return False
    settings = get_settings()
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if not settings.is_production and host in ("localhost", "127.0.0.1"):
        return True
    api_host = (urlparse(settings.api_public_url).hostname or "").lower()
    return bool(api_host and host == api_host)


def assert_https_url_allowed(url: str | None, *, field: str = "url") -> None:
    if not url or not str(url).strip():
        return
    if _is_lesson_video_file_url(str(url)):
        return
    parsed = urlparse(str(url).strip())
    if parsed.scheme != "https":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_url",
                "message": f"{field} must use HTTPS from an allowed host.",
            },
        )
    host = (parsed.hostname or "").lower()
    allowed = _allowed_hosts()
    if not host or host not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_url",
                "message": f"{field} host is not allowed.",
            },
        )


def is_https_url_allowed(url: str | None) -> bool:
    if not url or not str(url).strip():
        return False
    try:
        assert_https_url_allowed(url)
        return True
    except HTTPException:
        return False
