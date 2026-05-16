"""Optional startup DDL when SUPABASE_DB_PASSWORD is configured (dev/setup)."""

from __future__ import annotations

from pathlib import Path

from postgrest.exceptions import APIError

from app.config import get_settings
from app.db.client import get_supabase
from app.db.supabase_errors import is_missing_table_error
from app.debug_log import debug_log

MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "supabase" / "migrations"
CONTACT_MIGRATION = MIGRATIONS_DIR / "010_contact_submissions.sql"


def _contact_table_exists() -> bool:
    try:
        get_supabase().table("contact_submissions").select("id").limit(1).execute()
        return True
    except APIError as exc:
        if is_missing_table_error(exc, "contact_submissions"):
            return False
        raise


def _apply_sql_file(path: Path) -> None:
    import psycopg
    from urllib.parse import quote_plus

    settings = get_settings()
    password = settings.supabase_db_password
    if not password:
        raise RuntimeError("SUPABASE_DB_PASSWORD not set")

    ref = settings.supabase_url.replace("https://", "").replace(".supabase.co", "").strip("/")
    host = f"db.{ref}.supabase.co"
    dsn = f"postgresql://postgres:{quote_plus(password)}@{host}:5432/postgres?sslmode=require"
    sql = path.read_text(encoding="utf-8")
    if "NOTIFY pgrst" not in sql:
        sql = f"{sql.rstrip()}\nNOTIFY pgrst, 'reload schema';\n"

    with psycopg.connect(dsn) as conn:
        conn.execute(sql)
        conn.commit()


def ensure_contact_submissions() -> bool:
    """Return True if contact_submissions exists (or was created)."""
    # #region agent log
    debug_log(
        "db/schema_bootstrap.py:ensure_contact_submissions",
        "ensure_contact_submissions entry",
        {"migrationFile": str(CONTACT_MIGRATION.name)},
        hypothesis_id="C1",
        run_id="post-fix",
    )
    # #endregion

    if _contact_table_exists():
        # #region agent log
        debug_log(
            "db/schema_bootstrap.py:ensure_contact_submissions",
            "contact_submissions already exists",
            {},
            hypothesis_id="C1",
            run_id="post-fix",
        )
        # #endregion
        return True

    settings = get_settings()
    if not settings.supabase_db_password:
        # #region agent log
        debug_log(
            "db/schema_bootstrap.py:ensure_contact_submissions",
            "table missing; no SUPABASE_DB_PASSWORD for auto-migrate",
            {},
            hypothesis_id="C1",
            run_id="post-fix",
        )
        # #endregion
        return False

    if not CONTACT_MIGRATION.is_file():
        return False

    try:
        _apply_sql_file(CONTACT_MIGRATION)
    except Exception as exc:
        # #region agent log
        debug_log(
            "db/schema_bootstrap.py:ensure_contact_submissions",
            "auto-migrate failed",
            {"error": str(exc)[:200]},
            hypothesis_id="C2",
            run_id="post-fix",
        )
        # #endregion
        return False

    exists = _contact_table_exists()
    # #region agent log
    debug_log(
        "db/schema_bootstrap.py:ensure_contact_submissions",
        "auto-migrate finished",
        {"existsAfter": exists},
        hypothesis_id="C2",
        run_id="post-fix",
    )
    # #endregion
    return exists
