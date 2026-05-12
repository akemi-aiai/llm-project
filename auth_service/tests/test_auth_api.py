import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_full_flow(client: AsyncClient) -> None:
    register_response = await client.post(
        "/auth/register",
        json={"email": "student@example.com", "password": "StrongPassword123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "student@example.com"
    assert "password_hash" not in register_response.json()

    login_response = await client.post(
        "/auth/login",
        data={"username": "student@example.com", "password": "StrongPassword123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert login_response.json()["token_type"] == "bearer"

    me_response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "student@example.com"


@pytest.mark.asyncio
async def test_duplicate_registration_returns_409(client: AsyncClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "StrongPassword123"}
    first_response = await client.post("/auth/register", json=payload)
    second_response = await client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"email": "wrongpass@example.com", "password": "StrongPassword123"},
    )

    response = await client.post(
        "/auth/login",
        data={"username": "wrongpass@example.com", "password": "WrongPassword123"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token_or_with_bad_token_returns_401(client: AsyncClient) -> None:
    no_token_response = await client.get("/auth/me")
    bad_token_response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert no_token_response.status_code == 401
    assert bad_token_response.status_code == 401
