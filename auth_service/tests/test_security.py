from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hashing_and_verify() -> None:
    password = "StrongPassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


def test_create_and_decode_access_token() -> None:
    token = create_access_token(sub=123, role="user")
    payload = decode_token(token)

    assert payload["sub"] == "123"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload
