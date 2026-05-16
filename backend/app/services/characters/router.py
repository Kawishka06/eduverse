from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user_public
from app.models.character import CharacterCreate, CharacterPublic, CharacterUpdate
from app.models.user import UserPublic
from app.services.characters.service import CharacterService

router = APIRouter(prefix="/characters", tags=["characters"])


def get_character_service() -> CharacterService:
    return CharacterService()


@router.get("", response_model=list[CharacterPublic])
def list_characters(
    user: UserPublic = Depends(get_current_user_public),
    service: CharacterService = Depends(get_character_service),
) -> list[CharacterPublic]:
    return service.list_characters(str(user.id))


@router.get("/{character_id}", response_model=CharacterPublic)
def get_character(
    character_id: str,
    user: UserPublic = Depends(get_current_user_public),
    service: CharacterService = Depends(get_character_service),
) -> CharacterPublic:
    return service.get_character(str(user.id), character_id)


@router.post("", response_model=CharacterPublic, status_code=status.HTTP_201_CREATED)
async def create_character(
    payload: CharacterCreate,
    user: UserPublic = Depends(get_current_user_public),
    service: CharacterService = Depends(get_character_service),
) -> CharacterPublic:
    return await service.create_character(user, payload)


@router.patch("/{character_id}", response_model=CharacterPublic)
def update_character(
    character_id: str,
    payload: CharacterUpdate,
    user: UserPublic = Depends(get_current_user_public),
    service: CharacterService = Depends(get_character_service),
) -> CharacterPublic:
    return service.update_character(str(user.id), character_id, payload)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    character_id: str,
    user: UserPublic = Depends(get_current_user_public),
    service: CharacterService = Depends(get_character_service),
) -> None:
    service.delete_character(str(user.id), character_id)
