from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    personality: str = Field(default="", max_length=2000)
    teaching_style: str = Field(default="", max_length=1000)
    visual_description: str = Field(..., min_length=10, max_length=3000)
    voice_style: str = Field(default="friendly", max_length=200)
    class_tag: str | None = Field(default=None, max_length=120)
    visibility: str = Field(default="personal", pattern="^(personal|class)$")
    generate_art: bool = True


class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    personality: str | None = Field(default=None, max_length=2000)
    teaching_style: str | None = Field(default=None, max_length=1000)
    visual_description: str | None = Field(default=None, max_length=3000)
    voice_style: str | None = Field(default=None, max_length=200)
    class_tag: str | None = Field(default=None, max_length=120)
    visibility: str | None = Field(default=None, pattern="^(personal|class)$")


class CharacterPublic(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    personality: str
    teaching_style: str
    visual_description: str
    voice_style: str
    character_bible: str | None = None
    reference_image_url: str | None = None
    reference_sheet_urls: list[str] = Field(default_factory=list)
    class_tag: str | None = None
    visibility: str
    created_at: datetime

    model_config = {"from_attributes": True}
