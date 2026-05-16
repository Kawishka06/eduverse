"""File-based persistence for lesson characters, materials, and video jobs."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.config import get_settings

_STORE: "LessonFileStore | None" = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LessonFileStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.characters_dir = root / "characters"
        self.materials_dir = root / "materials"
        self.jobs_dir = root / "jobs"
        for d in (self.characters_dir, self.materials_dir, self.jobs_dir):
            d.mkdir(parents=True, exist_ok=True)

    # --- Characters ---

    def list_characters_accessible(self, user_id: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for path in self.characters_dir.glob("*.json"):
            row = self._read_json(path)
            if not row:
                continue
            oid = str(row.get("owner_id", ""))
            vis = row.get("visibility", "personal")
            if oid == user_id or vis == "class":
                rows.append(row)
        rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        return rows

    def get_character(self, character_id: str) -> dict[str, Any] | None:
        path = self.characters_dir / f"{character_id}.json"
        return self._read_json(path) if path.is_file() else None

    def create_character(self, row: dict[str, Any]) -> dict[str, Any]:
        cid = str(row.get("id") or uuid4())
        now = _utc_now()
        record = {
            "id": cid,
            "owner_id": str(row["owner_id"]),
            "name": row["name"],
            "personality": row.get("personality", ""),
            "teaching_style": row.get("teaching_style", ""),
            "visual_description": row.get("visual_description", ""),
            "voice_style": row.get("voice_style", "friendly"),
            "character_bible": row.get("character_bible"),
            "reference_image_url": row.get("reference_image_url"),
            "reference_sheet_urls": row.get("reference_sheet_urls") or [],
            "class_tag": row.get("class_tag"),
            "visibility": row.get("visibility", "personal"),
            "created_at": now,
            "updated_at": now,
        }
        self._write_json(self.characters_dir / f"{cid}.json", record)
        return record

    def update_character(self, character_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        row = self.get_character(character_id)
        if not row:
            raise KeyError(character_id)
        row.update(patch)
        row["updated_at"] = _utc_now()
        self._write_json(self.characters_dir / f"{character_id}.json", row)
        return row

    def delete_character(self, character_id: str) -> None:
        path = self.characters_dir / f"{character_id}.json"
        if path.is_file():
            path.unlink()

    @staticmethod
    def can_access_character(row: dict[str, Any], user_id: str) -> bool:
        if str(row.get("owner_id")) == user_id:
            return True
        return row.get("visibility") == "class"

    # --- Materials ---

    def list_materials(self, user_id: str) -> list[dict[str, Any]]:
        user_dir = self.materials_dir / user_id
        if not user_dir.is_dir():
            return []
        rows: list[dict[str, Any]] = []
        for meta_path in user_dir.glob("*/meta.json"):
            row = self._read_json(meta_path)
            if row:
                rows.append(row)
        rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        return rows

    def get_material(self, material_id: str) -> dict[str, Any] | None:
        for meta_path in self.materials_dir.glob(f"*/{material_id}/meta.json"):
            return self._read_json(meta_path)
        return None

    def material_file_path(self, material_id: str) -> Path | None:
        row = self.get_material(material_id)
        if not row:
            return None
        user_id = str(row["user_id"])
        path = self.materials_dir / user_id / material_id / "file"
        return path if path.is_file() else None

    def create_material(
        self,
        *,
        user_id: str,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        file_url: str | None = None,
        extracted_text: str | None = None,
    ) -> dict[str, Any]:
        mid = str(uuid4())
        material_dir = self.materials_dir / user_id / mid
        material_dir.mkdir(parents=True, exist_ok=True)
        (material_dir / "file").write_bytes(file_bytes)
        record = {
            "id": mid,
            "user_id": user_id,
            "filename": filename,
            "content_type": content_type,
            "storage_path": f"{user_id}/{mid}/file",
            "file_url": file_url or "",
            "extracted_text": extracted_text,
            "created_at": _utc_now(),
        }
        self._write_json(material_dir / "meta.json", record)
        return record

    def set_material_file_url(self, material_id: str, file_url: str) -> dict[str, Any]:
        row = self.get_material(material_id)
        if not row:
            raise KeyError(material_id)
        row["file_url"] = file_url
        user_id = str(row["user_id"])
        self._write_json(self.materials_dir / user_id / material_id / "meta.json", row)
        return row

    def update_material_text(self, material_id: str, text: str) -> dict[str, Any]:
        row = self.get_material(material_id)
        if not row:
            raise KeyError(material_id)
        row["extracted_text"] = text
        user_id = str(row["user_id"])
        self._write_json(self.materials_dir / user_id / material_id / "meta.json", row)
        return row

    def delete_material(self, material_id: str) -> None:
        row = self.get_material(material_id)
        if not row:
            return
        user_id = str(row["user_id"])
        material_dir = self.materials_dir / user_id / material_id
        if material_dir.is_dir():
            shutil.rmtree(material_dir, ignore_errors=True)

    # --- Video jobs ---

    def _job_path(self, user_id: str, job_id: str) -> Path:
        user_dir = self.jobs_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / f"{job_id}.json"

    def create_job(self, row: dict[str, Any]) -> dict[str, Any]:
        jid = str(row.get("id") or uuid4())
        user_id = str(row["user_id"])
        now = _utc_now()
        record = {
            "id": jid,
            "user_id": user_id,
            "material_id": row.get("material_id"),
            "character_id": row.get("character_id"),
            "status": row.get("status", "pending"),
            "progress": int(row.get("progress") or 0),
            "title": row.get("title", ""),
            "scenes_json": row.get("scenes_json") or [],
            "playlist_url": row.get("playlist_url"),
            "error_message": row.get("error_message"),
            "created_at": now,
            "updated_at": now,
        }
        self._write_json(self._job_path(user_id, jid), record)
        return record

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        for path in self.jobs_dir.glob(f"*/{job_id}.json"):
            return self._read_json(path)
        return None

    def update_job(self, job_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        row = self.get_job(job_id)
        if not row:
            raise KeyError(job_id)
        row.update(patch)
        row["updated_at"] = _utc_now()
        user_id = str(row["user_id"])
        self._write_json(self._job_path(user_id, job_id), row)
        return row

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any] | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, default=str), encoding="utf-8")


def get_lesson_file_store() -> LessonFileStore:
    global _STORE
    if _STORE is None:
        settings = get_settings()
        _STORE = LessonFileStore(settings.lesson_data_dir)
    return _STORE
