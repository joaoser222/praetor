from typing import List
from pathlib import Path
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Project root directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    APP_NAME: str = "Praetor"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000

    DATABASE_URL: str = Field(..., description="Database connection URL")
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Celery settings
    CELERY_BROKER_URL: str = Field("redis://localhost:6379/0", description="URL for Celery message broker (e.g., redis, amqp)")
    CELERY_RESULT_BACKEND: str = Field("redis://localhost:6379/1", description="URL for Celery result backend (e.g., redis, db+postgresql)")

    CORS_ORIGINS: List[AnyHttpUrl] = []

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_str(self) -> List[str]:
        return [str(u).rstrip("/") for u in self.CORS_ORIGINS]


settings = Settings()
