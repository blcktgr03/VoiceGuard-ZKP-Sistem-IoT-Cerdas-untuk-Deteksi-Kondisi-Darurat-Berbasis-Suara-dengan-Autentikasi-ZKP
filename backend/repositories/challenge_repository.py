from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.authentication_challenge import AuthenticationChallenge


class AuthenticationChallengeRepository:
    """Persist and consume short-lived Schnorr challenges."""

    def __init__(self, db: Session) -> None:
        """Create a repository with an active database session."""
        self._db = db

    def create(
        self,
        device_id: int,
        commitment: str,
        challenge: int,
        expires_at: datetime,
    ) -> AuthenticationChallenge:
        """Insert a challenge row."""
        record = AuthenticationChallenge(
            device_id=device_id,
            commitment=commitment,
            challenge=challenge,
            expires_at=expires_at,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def get_active(self, device_id: int, commitment: str) -> AuthenticationChallenge | None:
        """Return the newest unused, unexpired challenge for a device commitment."""
        now = datetime.now(timezone.utc)
        statement = (
            select(AuthenticationChallenge)
            .where(AuthenticationChallenge.device_id == device_id)
            .where(AuthenticationChallenge.commitment == commitment)
            .where(AuthenticationChallenge.used_at.is_(None))
            .where(AuthenticationChallenge.expires_at > now)
            .order_by(AuthenticationChallenge.created_at.desc())
        )
        return self._db.scalar(statement)

    def mark_used(self, challenge: AuthenticationChallenge) -> AuthenticationChallenge:
        """Mark a challenge as consumed."""
        challenge.used_at = datetime.now(timezone.utc)
        self._db.add(challenge)
        self._db.commit()
        self._db.refresh(challenge)
        return challenge
