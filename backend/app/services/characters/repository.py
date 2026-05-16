from __future__ import annotations

from typing import Any

from app.services.lesson.file_store import get_lesson_file_store


class CharacterRepository:
    def __init__(self) -> None:
        self._store = get_lesson_file_store()

    def list_accessible(self, user_id: str) -> list[dict[str, Any]]:
        return self._store.list_characters_accessible(user_id)

    def get_by_id(self, character_id: str) -> dict[str, Any] | None:
        return self._store.get_character(character_id)

    def create(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._store.create_character(row)

    def update(self, character_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        return self._store.update_character(character_id, patch)

    def delete(self, character_id: str) -> None:
        self._store.delete_character(character_id)

    def can_access(self, row: dict[str, Any], user_id: str) -> bool:
        return self._store.can_access_character(row, user_id)
