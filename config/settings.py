from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from typing import List, Optional
from pathlib import Path
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_app_version() -> str:
    """Versão da aplicação — fonte única em `pyproject.toml` (fallback sem install)."""
    try:
        return package_version("praetor")
    except PackageNotFoundError:
        return "0.1.0"


class Settings(BaseSettings):
    # Diretório raiz do projeto
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    APP_NAME: str = "Praetor"
    APP_VERSION: str = _default_app_version()
    DEBUG: bool = False

    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000

    DATABASE_URL: str = Field(..., description="Database connection URL")
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ALGORITHM: str = "HS256"
    # Curto de propósito: o access é um JWT stateless e não pode ser revogado
    # antes do `exp`, então este valor define a janela máxima em que um token
    # "deslogado" ainda é aceito. A renovação é transparente via refresh cookie.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Cookies de auth: quando None, o atributo Secure é derivado de DEBUG
    # (ligado fora de desenvolvimento). Defina explicitamente (ex.:
    # COOKIE_SECURE=false) caso a app seja servida por HTTP fora de localhost.
    COOKIE_SECURE: Optional[bool] = None

    # Configurações do Celery
    CELERY_BROKER_URL: str = Field("redis://localhost:6379/0", description="URL for Celery message broker (e.g., redis, amqp)")
    CELERY_RESULT_BACKEND: str = Field("redis://localhost:6379/1", description="URL for Celery result backend (e.g., redis, db+postgresql)")

    CORS_ORIGINS: List[AnyHttpUrl] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Ignora variáveis de ambiente sem campo correspondente (ex.: POSTGRES_*,
        # SERVER_*, HOSTNAME). Sem isto, um .env compartilhado com o Docker quebra
        # a aplicação em runtime.
        extra="ignore",
    )

    @property
    def cors_origins_str(self) -> List[str]:
        return [str(u).rstrip("/") for u in self.CORS_ORIGINS]

    @property
    def cookie_secure(self) -> bool:
        """Indica se os cookies de auth devem usar o atributo Secure."""
        if self.COOKIE_SECURE is not None:
            return self.COOKIE_SECURE
        return not self.DEBUG


settings = Settings()
