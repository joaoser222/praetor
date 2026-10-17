from pathlib import Path
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.database import get_db
from core.base_model import BaseModel

# Importar a aplicação dispara a auto-descoberta dos apps e,
# consequentemente, a importação dos models (populando BaseModel.metadata).
from main import app

# Banco de dados SQLite em arquivo dedicado aos testes. Caminho absoluto para não
# depender do diretório de trabalho.
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{Path(__file__).resolve().parent / 'test.db'}"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Cria um banco limpo e fornece uma sessão para cada teste."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Fornece um cliente HTTP assíncrono com a dependência de banco sobrescrita."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client
    app.dependency_overrides.clear()
