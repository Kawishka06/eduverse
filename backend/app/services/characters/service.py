from __future__ import annotations

from fastapi import HTTPException, status

from app.models.character import CharacterCreate, CharacterPublic, CharacterUpdate
from app.models.user import UserPublic
from app.services.ai.orchestrator import AIOrchestrator, get_ai_orchestrator
from app.services.characters.repository import CharacterRepository


class CharacterService:
    def __init__(self, orchestrator: AIOrchestrator | None = None):
        self.repo = CharacterRepository()
        self.orchestrator = orchestrator or get_ai_orchestrator()

    def list_characters(self, user_id: str) -> list[CharacterPublic]:
        rows = self.repo.list_accessible(user_id)
        return [CharacterPublic.model_validate(r) for r in rows]

    def get_character(self, user_id: str, character_id: str) -> CharacterPublic:
        row = self.repo.get_by_id(character_id)
        if not row or not self.repo.can_access(row, user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
        return CharacterPublic.model_validate(row)

    async def create_character(
        self,
        user: UserPublic,
        payload: CharacterCreate,
    ) -> CharacterPublic:
        if payload.visibility == "class" and user.role.value not in ("teacher", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can publish class characters",
            )

        bible = await self.orchestrator.design_character_bible(
            name=payload.name,
            personality=payload.personality,
            teaching_style=payload.teaching_style,
            visual_description=payload.visual_description,
            voice_style=payload.voice_style,
        )

        reference_url: str | None = None
        sheet_urls: list[str] = []
        if payload.generate_art:
            reference_url, sheet_urls = await self.orchestrator.generate_character_reference(
                bible,
                owner_id=str(user.id),
            )

        row = self.repo.create(
            {
                "owner_id": str(user.id),
                "name": payload.name.strip(),
                "personality": payload.personality.strip(),
                "teaching_style": payload.teaching_style.strip(),
                "visual_description": payload.visual_description.strip(),
                "voice_style": payload.voice_style.strip(),
                "character_bible": bible,
                "reference_image_url": reference_url,
                "reference_sheet_urls": sheet_urls,
                "class_tag": payload.class_tag,
                "visibility": payload.visibility,
            },
        )
        return CharacterPublic.model_validate(row)

    def update_character(
        self,
        user_id: str,
        character_id: str,
        payload: CharacterUpdate,
    ) -> CharacterPublic:
        row = self.repo.get_by_id(character_id)
        if not row or str(row["owner_id"]) != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

        patch = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
        if patch.get("visibility") == "class":
            from app.services.auth.repository import ProfileRepository

            profile = ProfileRepository().get_by_id(user_id)
            role = profile.role.value if profile else "student"
            if role not in ("teacher", "admin"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only teachers can publish class characters",
                )
        updated = self.repo.update(character_id, patch)
        return CharacterPublic.model_validate(updated)

    def delete_character(self, user_id: str, character_id: str) -> None:
        row = self.repo.get_by_id(character_id)
        if not row or str(row["owner_id"]) != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
        self.repo.delete(character_id)

    def persona_for_agent(self, character_id: str | None, user_id: str) -> str | None:
        if not character_id:
            return None
        row = self.repo.get_by_id(character_id)
        if not row or not self.repo.can_access(row, user_id):
            return None
        bible = row.get("character_bible") or ""
        name = row.get("name", "Tutor")
        return f"You are {name}. {bible}".strip()
