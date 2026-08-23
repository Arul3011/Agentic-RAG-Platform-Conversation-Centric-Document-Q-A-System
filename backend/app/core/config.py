from pydantic_settings import BaseSettings
from pydantic import field_validator
import os


class Settings(BaseSettings):
    APP_NAME: str = "Agentic-RAG"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "agentic_rag"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    DATABASE_URL: str = ""

    VECTOR_DB_TYPE: str = "pgvector"
    VECTOR_DIMENSION: int = 3072

    GEMINI_API_KEY: str = ""
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-2"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"
    OPENROUTER_AGENT_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"
    OPENROUTER_SUMMARY_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"

    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 100

    TOP_K: int = 10
    FINAL_CONTEXT_K: int = 5
    VECTOR_SEARCH_ENABLED: bool = True
    KEYWORD_SEARCH_ENABLED: bool = True
    METADATA_SEARCH_ENABLED: bool = True
    HYBRID_SEARCH_ENABLED: bool = True

    MAX_HISTORY_MESSAGES: int = 20
    SUMMARY_TRIGGER_MESSAGES: int = 20

    MAX_FILE_SIZE_MB: int = 25
    UPLOAD_DIRECTORY: str = "./uploads"

    LOG_LEVEL: str = "INFO"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str, info) -> str:
        if v:
            return v
        data = info.data
        return (
            f"postgresql+psycopg://{data.get('POSTGRES_USER')}:"
            f"{data.get('POSTGRES_PASSWORD')}@{data.get('POSTGRES_HOST')}:"
            f"{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"
        )

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
