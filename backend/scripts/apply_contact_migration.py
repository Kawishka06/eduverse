"""Apply migration 010 (contact_submissions) via direct Postgres connection.

Requires SUPABASE_DB_PASSWORD in backend/.env (Supabase Dashboard → Project Settings → Database).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "supabase" / "migrations" / "010_contact_submissions.sql"


def main() -> int:
    try:
        import psycopg
    except ImportError:
        print("Install psycopg: pip install 'psycopg[binary]'")
        return 1

    from app.config import get_settings

    settings = get_settings()
    password = getattr(settings, "supabase_db_password", None) or ""
    if not password:
        print(
            "Missing SUPABASE_DB_PASSWORD in backend/.env\n"
            "Get it from Supabase Dashboard → Project Settings → Database → Database password"
        )
        return 1

    ref = settings.supabase_url.replace("https://", "").replace(".supabase.co", "").strip("/")
    host = f"db.{ref}.supabase.co"
    dsn = f"postgresql://postgres:{password}@{host}:5432/postgres?sslmode=require"
    sql = MIGRATION.read_text(encoding="utf-8")

    print(f"Applying {MIGRATION.name} to {host} ...")
    with psycopg.connect(dsn) as conn:
        conn.execute(sql)
        conn.commit()
    print("Done. contact_submissions table created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
