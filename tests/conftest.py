import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.database import get_db
from core.base_model import BaseModel
from main import app

# Usa um banco de dados SQLite em memória para os testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest.fixture(scope="session")
def event_loop():
    """Cria uma instância do event loop padrão para cada sessão de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Fixture que cria uma nova sessão de banco de dados para cada teste."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)



@pytest.fixture(scope="function")
def client(db: AsyncSession) -> TestClient:
    """Fixture que cria um TestClient com a dependência de banco de dados sobrescrita."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
