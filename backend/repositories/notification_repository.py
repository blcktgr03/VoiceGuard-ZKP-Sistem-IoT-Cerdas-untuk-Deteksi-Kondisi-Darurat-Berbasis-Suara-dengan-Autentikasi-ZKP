from sqlalchemy.orm import Session

from backend.models.notification import Notification


class NotificationRepository:
    """Persist notification delivery attempts."""

    def __init__(self, db: Session) -> None:
        """Create a repository with an active database session."""
        self._db = db

    def create(
        self,
        classification_id: int,
        channel: str,
        recipient: str,
        message: str,
        status: str,
    ) -> Notification:
        """Insert a notification row."""
        notification = Notification(
            classification_id=classification_id,
            channel=channel,
            recipient=recipient,
            message=message,
            status=status,
        )
        self._db.add(notification)
        self._db.commit()
        self._db.refresh(notification)
        return notification
