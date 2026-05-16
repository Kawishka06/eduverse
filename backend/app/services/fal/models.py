from pydantic import BaseModel, Field


class ImageGenerationResult(BaseModel):
    url: str
    prompt: str
    model: str
    mock: bool = False


class VideoGenerationResult(BaseModel):
    url: str
    source_image_url: str
    model: str
    mock: bool = False


class ImageToTextResult(BaseModel):
    text: str
    image_url: str
    model: str
    mock: bool = False


class TextToSpeechResult(BaseModel):
    audio_url: str
    text: str
    model: str
    mock: bool = False


class FalRawResponse(BaseModel):
    """Wrapper for raw fal.ai JSON before parsing."""

    data: dict = Field(default_factory=dict)
    model: str
    mock: bool = False
