from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from backend.api.schemas import AuthProofRequest, ChallengeRequest
from backend.auth.tokens import AuthTokenService
from backend.config.settings import get_settings
from backend.repositories.auth_repository import AuthenticationLogRepository
from backend.repositories.challenge_repository import AuthenticationChallengeRepository
from backend.repositories.device_repository import DeviceRepository
from backend.zkp.service import ZkpService


@dataclass(frozen=True)
class AuthenticationResult:
    """Result returned after Schnorr proof verification."""

    authenticated: bool
    reason: str
    device_db_id: int | None = None
    auth_token: str | None = None


@dataclass(frozen=True)
class ChallengeResult:
    """Challenge data returned to a device."""

    device_id: str
    challenge: int
    expires_at: datetime


class AuthenticationService:
    """Coordinate Schnorr challenge creation and proof verification."""

    def __init__(
        self,
        devices: DeviceRepository,
        challenges: AuthenticationChallengeRepository,
        logs: AuthenticationLogRepository,
        zkp: ZkpService,
        tokens: AuthTokenService,
    ) -> None:
        """Create an authentication service from repositories and security helpers."""
        self._devices = devices
        self._challenges = challenges
        self._logs = logs
        self._zkp = zkp
        self._tokens = tokens
        self._settings = get_settings()

    def request_challenge(self, payload: ChallengeRequest) -> ChallengeResult | None:
        """Create a challenge for a registered device commitment."""
        device = self._devices.get_by_device_id(payload.device_id)
        if device is None:
            return None

        challenge = self._zkp.generate_challenge()
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=self._settings.challenge_ttl_seconds
        )
        self._challenges.create(
            device_id=device.id,
            commitment=payload.commitment,
            challenge=challenge,
            expires_at=expires_at,
        )
        return ChallengeResult(
            device_id=device.device_id,
            challenge=challenge,
            expires_at=expires_at,
        )

    def verify_device(self, proof: AuthProofRequest) -> AuthenticationResult:
        """Verify a device proof and issue an upload token when valid."""
        device = self._devices.get_by_device_id(proof.device_id)
        if device is None:
            self._logs.create(
                device_id=None,
                commitment=proof.commitment,
                challenge="",
                response=proof.response,
                is_success=False,
                reason="Unknown device.",
            )
            return AuthenticationResult(False, "Unknown device.")

        challenge_record = self._challenges.get_active(device.id, proof.commitment)
        if challenge_record is None:
            self._logs.create(
                device_id=device.id,
                commitment=proof.commitment,
                challenge="",
                response=proof.response,
                is_success=False,
                reason="Missing, expired, or already used challenge.",
            )
            return AuthenticationResult(False, "Missing, expired, or already used challenge.")

        is_valid = self._zkp.verify(
            public_key=device.public_key,
            commitment=proof.commitment,
            challenge=challenge_record.challenge,
            response=proof.response,
        )
        reason = "Authentication accepted." if is_valid else "Invalid proof."
        if is_valid:
            self._challenges.mark_used(challenge_record)

        token = self._tokens.issue(device.id, device.device_id) if is_valid else None
        self._logs.create(
            device_id=device.id,
            commitment=proof.commitment,
            challenge=str(challenge_record.challenge),
            response=proof.response,
            is_success=is_valid,
            reason=reason,
        )
        return AuthenticationResult(
            is_valid,
            reason,
            device.id if is_valid else None,
            token,
        )
