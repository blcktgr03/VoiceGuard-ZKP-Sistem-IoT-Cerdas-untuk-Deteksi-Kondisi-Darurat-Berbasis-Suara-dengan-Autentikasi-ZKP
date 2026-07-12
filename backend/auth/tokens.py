import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedDevice:
    """Device identity extracted from a valid authentication token."""

    device_db_id: int
    device_id: str


class AuthTokenService:
    """Issue and verify signed short-lived upload tokens."""

    def __init__(self, secret: str, ttl_seconds: int) -> None:
        """Create a token service with an HMAC secret and TTL."""
        self._secret = secret.encode("utf-8")
        self._ttl_seconds = ttl_seconds

    def issue(self, device_db_id: int, device_id: str) -> str:
        """Create a signed token for an authenticated device."""
        payload = {
            "sub": device_id,
            "device_db_id": device_db_id,
            "exp": int(time.time()) + self._ttl_seconds,
        }
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        payload_part = self._b64encode(payload_bytes)
        signature = self._sign(payload_part)
        return f"{payload_part}.{signature}"

    def verify(self, token: str) -> AuthenticatedDevice | None:
        """Verify a token and return its device identity."""
        try:
            payload_part, signature = token.split(".", maxsplit=1)
        except ValueError:
            return None

        expected_signature = self._sign(payload_part)
        if not hmac.compare_digest(signature, expected_signature):
            return None

        try:
            payload = json.loads(self._b64decode(payload_part))
        except (ValueError, json.JSONDecodeError):
            return None

        if int(payload.get("exp", 0)) < int(time.time()):
            return None

        return AuthenticatedDevice(
            device_db_id=int(payload["device_db_id"]),
            device_id=str(payload["sub"]),
        )

    def _sign(self, payload_part: str) -> str:
        """Create the HMAC signature for a token payload."""
        signature = hmac.new(self._secret, payload_part.encode("utf-8"), hashlib.sha256).digest()
        return self._b64encode(signature)

    @staticmethod
    def _b64encode(value: bytes) -> str:
        """Encode bytes with URL-safe base64 without padding."""
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @staticmethod
    def _b64decode(value: str) -> bytes:
        """Decode URL-safe base64 with restored padding."""
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
