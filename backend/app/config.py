
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodePilot"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:5173"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-001"

    qdrant_path: str = "./qdrant_data"
    qdrant_collection: str = "codebase"

    rag_top_k: int = 4
    rag_min_score: float = 0.58

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()