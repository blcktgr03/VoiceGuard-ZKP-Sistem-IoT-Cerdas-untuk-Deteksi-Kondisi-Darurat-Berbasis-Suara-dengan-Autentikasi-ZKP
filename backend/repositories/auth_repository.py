from sqlalchemy.orm import Session

from backend.models.authentication_log import AuthenticationLog


class AuthenticationLogRepository:
    """Persist Schnorr authentication attempts."""

    def __init__(self, db: Session) -> None:
        """Create a repository with an active database session."""
        self._db = db

    def create(
        self,
        device_id: int | None,
        commitment: str,
        challenge: str,
        response: str,
        is_success: bool,
        reason: str,
    ) -> AuthenticationLog:
        """Insert an authentication log row."""
        log = AuthenticationLog(
            device_id=device_id,
            commitment=commitment,
            challenge=challenge,
            response=response,
            is_success=is_success,
            reason=reason,
        )
        self._db.add(log)
        self._db.commit()
        self._db.refresh(log)
        return log
