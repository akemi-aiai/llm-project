from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from jose import jwt

from app.bot.handlers import text_handler, token_handler, token_key
from app.core.config import settings
from tests.conftest import FakeMessage


def make_test_token(sub: str = "123", role: str = "user") -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": sub,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )


@pytest.mark.asyncio
async def test_token_handler_saves_valid_token(monkeypatch, fake_redis) -> None:
    async def fake_get_redis():
        return fake_redis

    monkeypatch.setattr("app.bot.handlers.get_redis", fake_get_redis)

    token = make_test_token()
    message = FakeMessage(text=f"/token {token}")

    await token_handler(message)

    saved_token = await fake_redis.get(token_key(message.from_user.id))
    assert saved_token == token
    assert "Этот токен мне нравится, я сохранил." in message.answers[0]


@pytest.mark.asyncio
async def test_text_handler_without_token_does_not_call_celery(monkeypatch, fake_redis) -> None:
    async def fake_get_redis():
        return fake_redis

    monkeypatch.setattr("app.bot.handlers.get_redis", fake_get_redis)
    delay_mock = Mock()
    monkeypatch.setattr("app.bot.handlers.llm_request.delay", delay_mock)

    message = FakeMessage(text="Hello")
    await text_handler(message)

    delay_mock.assert_not_called()
    assert "Дальше дороги нет" in message.answers[0]


@pytest.mark.asyncio
async def test_text_handler_with_token_calls_celery(monkeypatch, fake_redis) -> None:
    async def fake_get_redis():
        return fake_redis

    monkeypatch.setattr("app.bot.handlers.get_redis", fake_get_redis)
    delay_mock = Mock()
    monkeypatch.setattr("app.bot.handlers.llm_request.delay", delay_mock)

    message = FakeMessage(text="Explain JWT")
    token = make_test_token()
    await fake_redis.set(token_key(message.from_user.id), token)

    await text_handler(message)

    delay_mock.assert_called_once_with(message.chat.id, "Explain JWT")
    assert "Я отправил ваш запрос" in message.answers[0]
