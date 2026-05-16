#!/usr/bin/env python3
"""Create lesson-materials and lesson-characters storage buckets via Supabase API."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND))

from app.config import get_settings
from supabase import create_client


def main() -> int:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        print("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in backend/.env")
        return 1

    client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    for name in ("lesson-materials", "lesson-characters"):
        try:
            client.storage.create_bucket(name, options={"public": True})
            print(f"Created bucket: {name}")
        except Exception as exc:
            if "already exists" in str(exc).lower() or "duplicate" in str(exc).lower():
                print(f"Bucket exists: {name}")
            else:
                print(f"{name}: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
