from __future__ import annotations

import json
from typing import Any

from app.services.lesson.file_store import get_lesson_file_store


class LessonVideoJobRepository:
    def __init__(self) -> None:
        self._store = get_lesson_file_store()

    def create(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._store.create_job(row)

    def get(self, job_id: str) -> dict[str, Any] | None:
        return self._store.get_job(job_id)

    def update(self, job_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        return self._store.update_job(job_id, patch)

    def set_progress(self, job_id: str, progress: int, status: str | None = None) -> None:
        patch: dict[str, Any] = {"progress": progress}
        if status:
            patch["status"] = status
        self.update(job_id, patch)

    def scenes_from_row(self, row: dict[str, Any]) -> list[dict[str, Any]]:
        raw = row.get("scenes_json") or []
        if isinstance(raw, str):
            return json.loads(raw)
        return list(raw)
