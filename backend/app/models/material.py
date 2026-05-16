from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MaterialPublic(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    content_type: str
    file_url: str
    extracted_text: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
