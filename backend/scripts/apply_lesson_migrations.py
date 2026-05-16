#!/usr/bin/env python3
"""Apply lesson migrations (007 + 008). Prompts for DB password if not in .env."""

from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
_ROOT = _BACKEND.parent
sys.path.insert(0, str(_BACKEND))

try:
    from dotenv import load_dotenv

    load_dotenv(_BACKEND / ".env")
except ImportError:
    pass


def main() -> int:
    from app.config import get_settings
    from app.db.run_lesson_migrations import apply_lesson_migrations, ensure_lesson_buckets, lesson_tables_exist

    settings = get_settings()
    if lesson_tables_exist():
        print("Lesson tables already exist.")
        return 0

    if not settings.supabase_db_url.strip() and not settings.supabase_db_password.strip():
        print(
            "No SUPABASE_DB_URL or SUPABASE_DB_PASSWORD in backend/.env.\n"
            "Enter your Supabase database password (Dashboard -> Settings -> Database).\n"
            "It is NOT the anon or service_role key.\n",
        )
        pwd = getpass.getpass("Database password: ").strip()
        if not pwd:
            print("Cancelled.")
            return 1
        os.environ["SUPABASE_DB_PASSWORD"] = pwd
        get_settings.cache_clear()
        settings = get_settings()

    print("Applying migrations...")
    ensure_lesson_buckets(settings)
    if apply_lesson_migrations(settings):
        print("Success. Restart the backend and refresh Characters / Lesson Studio.")
        return 0

    print(
        "\nCould not connect to Postgres. Either:\n"
        "  1. Paste supabase/RUN_LESSON_MIGRATIONS.sql in Supabase SQL Editor and Run\n"
        "  2. Set SUPABASE_DB_URL to the full connection URI from Supabase Dashboard\n",
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
