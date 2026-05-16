from __future__ import annotations

from typing import Any

from app.services.lesson.file_store import get_lesson_file_store


class MaterialsRepository:
    def __init__(self) -> None:
        self._store = get_lesson_file_store()

    def list_for_user(self, user_id: str) -> list[dict[str, Any]]:
        return self._store.list_materials(user_id)

    def get_by_id(self, material_id: str) -> dict[str, Any] | None:
        return self._store.get_material(material_id)

    def create(self, row: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Use MaterialsService.upload_material")

    def create_with_file(
        self,
        *,
        user_id: str,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        extracted_text: str | None = None,
    ) -> dict[str, Any]:
        return self._store.create_material(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            file_bytes=file_bytes,
            extracted_text=extracted_text,
        )

    def set_file_url(self, material_id: str, file_url: str) -> dict[str, Any]:
        return self._store.set_material_file_url(material_id, file_url)

    def update_extracted_text(self, material_id: str, text: str) -> dict[str, Any]:
        return self._store.update_material_text(material_id, text)

    def delete(self, material_id: str) -> None:
        self._store.delete_material(material_id)

    def file_path(self, material_id: str):
        return self._store.material_file_path(material_id)
