from dataclasses import dataclass, field

import fakeredis.aioredis
import pytest


@pytest.fixture
async def fake_redis():
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis
    await redis.aclose()


@dataclass
class FakeUser:
    id: int


@dataclass
class FakeChat:
    id: int


@dataclass
class FakeMessage:
    text: str
    from_user: FakeUser = field(default_factory=lambda: FakeUser(id=42))
    chat: FakeChat = field(default_factory=lambda: FakeChat(id=777))
    answers: list[str] = field(default_factory=list)

    async def answer(self, text: str) -> None:
        self.answers.append(text)
