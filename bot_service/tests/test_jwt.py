from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


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


def test_decode_and_validate_valid_token() -> None:
    token = make_test_token(sub="123")
    payload = decode_and_validate(token)

    assert payload["sub"] == "123"
    assert payload["role"] == "user"


def test_decode_and_validate_invalid_token_raises_value_error() -> None:
    with pytest.raises(ValueError):
        decode_and_validate("not-a-jwt-token")
