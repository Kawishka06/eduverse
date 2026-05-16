from pydantic import BaseModel, Field


class MemeResult(BaseModel):
    image_url: str
    prompt: str
    model: str


class VideoResult(BaseModel):
    video_url: str
    source_image: str
    model: str


class TutorResult(BaseModel):
    answer: str
    question: str
    model: str
    mode: str = "standard"
    context_used: bool = False


class FalJobMeta(BaseModel):
    request_id: str | None = None
    model: str
