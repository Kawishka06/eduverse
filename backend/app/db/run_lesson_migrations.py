"""Apply lesson feature SQL migrations when DB credentials are available."""

from __future__ import annotations

import logging
from pathlib import Path

from app.config import Settings, get_settings
from app.db.health_check import probe_table

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[3]
_SQL_FILE = _ROOT / "supabase" / "RUN_LESSON_MIGRATIONS.sql"


def lesson_tables_exist() -> bool:
    return all(probe_table(t).get("exists") for t in ("lesson_characters", "lesson_materials", "lesson_video_jobs"))


def _build_connection_urls(settings: Settings) -> list[str]:
    urls: list[str] = []
    if settings.supabase_db_url.strip():
        urls.append(settings.supabase_db_url.strip())

    password = settings.supabase_db_password.strip()
    if not password or not settings.supabase_url.strip():
        return urls

    ref = settings.supabase_url.replace("https://", "").replace("http://", "").split(".")[0]
    hosts = [
        f"db.{ref}.supabase.co",
        f"aws-0-us-east-1.pooler.supabase.com",
        f"aws-0-us-west-1.pooler.supabase.com",
        f"aws-0-eu-west-1.pooler.supabase.com",
        f"aws-0-ap-southeast-1.pooler.supabase.com",
    ]
    for host in hosts:
        if host.startswith("db."):
            urls.append(f"postgresql://postgres:{password}@{host}:5432/postgres")
        else:
            urls.append(
                f"postgresql://postgres.{ref}:{password}@{host}:6543/postgres?sslmode=require",
            )
    return urls


def apply_lesson_migrations(settings: Settings | None = None) -> bool:
    """Return True if tables exist after this call (or already existed)."""
    settings = settings or get_settings()

    if lesson_tables_exist():
        return True

    if not _SQL_FILE.is_file():
        logger.error("Missing migration file: %s", _SQL_FILE)
        return False

    urls = _build_connection_urls(settings)
    if not urls:
        logger.warning(
            "Lesson tables missing. Add SUPABASE_DB_URL or SUPABASE_DB_PASSWORD to backend/.env "
            "(Supabase Dashboard -> Settings -> Database), or run supabase/RUN_LESSON_MIGRATIONS.sql "
            "in the SQL Editor.",
        )
        return False

    try:
        import psycopg2
    except ImportError:
        logger.error("Install psycopg2-binary to auto-apply migrations")
        return False

    sql = _SQL_FILE.read_text(encoding="utf-8")
    last_error: Exception | None = None

    for url in urls:
        try:
            conn = psycopg2.connect(url, connect_timeout=15)
            conn.autocommit = True
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
            finally:
                conn.close()
            if lesson_tables_exist():
                logger.info("Lesson feature migrations applied successfully")
                return True
        except Exception as exc:
            last_error = exc
            logger.debug("Migration connect failed for %s: %s", url.split("@")[-1], exc)

    logger.error("Could not apply lesson migrations: %s", last_error)
    return False


def ensure_lesson_buckets(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return
    try:
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        for name in ("lesson-materials", "lesson-characters"):
            try:
                client.storage.create_bucket(name, options={"public": True})
            except Exception:
                pass
    except Exception as exc:
        logger.debug("Bucket ensure skipped: %s", exc)
