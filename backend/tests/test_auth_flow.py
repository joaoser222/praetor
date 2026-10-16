"""Testes de contrato do fluxo de autenticação (golden path)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.schemas.user import UserCreate
from apps.auth.services.user import UserService

REGISTER_PAYLOAD = {
    "email": "user@example.com",
    "username": "user",
    "password": "secret123",
    "full_name": "Regular User",
}


async def _register_and_login(client, payload=REGISTER_PAYLOAD):
    response = await client.post("/api/auth/action/register", json=payload)
    assert response.status_code == 201, response.text
    response = await client.post(
        "/api/auth/action/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.asyncio
async def test_register_login_profile_refresh_logout(client):
    tokens = await _register_and_login(client)
    assert client.cookies.get("access_token"), "login deveria gravar o cookie HttpOnly"
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.get("/api/auth/action/profile", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]

    response = await client.post(
        "/api/auth/action/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200, response.text
    rotated = response.json()

    response = await client.post(
        "/api/auth/action/logout",
        json={"refresh_token": rotated["refresh_token"]},
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_profile_authenticates_via_httponly_cookie(client):
    """O cookie HttpOnly gravado no login deve autenticar sem header Authorization."""
    await _register_and_login(client)

    response = await client.get("/api/auth/action/profile")
    assert response.status_code == 200, response.text
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


@pytest.mark.asyncio
async def test_profile_requires_authentication(client):
    """Sem header e sem cookie, o endpoint protegido responde 401."""
    response = await client.get("/api/auth/action/profile")
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_refresh_and_logout_via_cookie_only(client):
    """Refresh e logout funcionam só com os cookies HttpOnly (sem corpo)."""
    await _register_and_login(client)

    response = await client.post("/api/auth/action/refresh")
    assert response.status_code == 200, response.text

    response = await client.post("/api/auth/action/logout")
    assert response.status_code == 200, response.text

    # Depois do logout os cookies são limpos e o endpoint protegido rejeita.
    response = await client.get("/api/auth/action/profile")
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_refresh_without_token_rejected(client):
    """Sem corpo e sem cookie, o refresh responde 401."""
    response = await client.post("/api/auth/action/refresh")
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_register_cannot_escalate_to_superuser(client):
    payload = {**REGISTER_PAYLOAD, "is_superuser": True}
    response = await client.post("/api/auth/action/register", json=payload)
    assert response.status_code == 201, response.text
    assert response.json()["is_superuser"] is False


@pytest.mark.asyncio
async def test_superuser_can_manage_users(client, db: AsyncSession):
    service = UserService(db)
    superuser = await service.create_user(
        UserCreate(
            email="admin@example.com",
            username="admin",
            password="secret123",
            full_name="Admin",
            is_superuser=True,
        )
    )

    response = await client.post(
        "/api/auth/action/login",
        data={"username": "admin@example.com", "password": "secret123"},
    )
    assert response.status_code == 200, response.text
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    response = await client.get("/api/auth/user/", headers=headers)
    assert response.status_code == 200, response.text
    assert any(u["id"] == superuser.id for u in response.json())

    response = await client.get(f"/api/auth/user/{superuser.id}", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["id"] == superuser.id

    response = await client.delete(f"/api/auth/user/{superuser.id}", headers=headers)
    assert response.status_code == 204, response.text
