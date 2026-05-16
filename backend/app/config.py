from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./eduverse.db"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # fal.ai / AI Orchestrator
    fal_key: str = ""
    fal_mock_mode: bool = False
    fal_meme_model: str = "fal-ai/flux/schnell"
    fal_image_model: str = "fal-ai/flux/schnell"
    fal_video_model: str = "fal-ai/minimax-video/image-to-video"
    fal_vision_model: str = "fal-ai/florence-2-large/caption"
    fal_tts_model: str = "fal-ai/kokoro/american-english"
    fal_llm_endpoint: str = "fal-ai/any-llm"
    fal_llm_model: str = "google/gemini-2.0-flash-001"
    fal_llm_max_tokens: int = 1024
    fal_request_timeout: float = 120.0

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Paths that skip JWT middleware (prefix match)
    public_paths: tuple[str, ...] = (
        "/register",
        "/login",
        "/ai/meme",
        "/ai/tutor",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
