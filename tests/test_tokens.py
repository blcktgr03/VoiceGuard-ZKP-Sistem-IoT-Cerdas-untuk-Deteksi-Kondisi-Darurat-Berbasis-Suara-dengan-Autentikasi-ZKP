from backend.auth.tokens import AuthTokenService


def test_auth_token_roundtrip() -> None:
    """Issue and verify an upload token."""
    service = AuthTokenService("test-secret", ttl_seconds=60)

    token = service.issue(device_db_id=1, device_id="esp8266-worker-01")
    authenticated = service.verify(token)

    assert authenticated is not None
    assert authenticated.device_db_id == 1
    assert authenticated.device_id == "esp8266-worker-01"


def test_auth_token_rejects_tampering() -> None:
    """Reject tokens whose payload or signature has been changed."""
    service = AuthTokenService("test-secret", ttl_seconds=60)
    token = service.issue(device_db_id=1, device_id="esp8266-worker-01")

    assert service.verify(token + "x") is None

