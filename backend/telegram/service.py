import logging

import httpx

from backend.config.settings import get_settings
from backend.models.classification import Classification
from backend.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """Send emergency alerts to Telegram and record delivery status."""

    def __init__(self, repository: NotificationRepository) -> None:
        """Create the service with a notification repository."""
        self._repository = repository
        self._settings = get_settings()

    def send_emergency_alert(
        self,
        classification: Classification,
        message: str,
    ):
        """Send a Telegram alert for an emergency classification."""
        if not self._settings.telegram_bot_token or not self._settings.telegram_chat_id:
            logger.warning("Telegram configuration is missing; notification is skipped.")
            return self._repository.create(
                classification_id=classification.id,
                channel="telegram",
                recipient="unconfigured",
                message=message,
                status="skipped",
            )

        recipient = self._settings.telegram_chat_id
        status = "sent"
        try:
            response = httpx.post(
                f"https://api.telegram.org/bot{self._settings.telegram_bot_token}/sendMessage",
                json={"chat_id": recipient, "text": message},
                timeout=10.0,
            )
            response.raise_for_status()
            logger.info("Telegram notification sent for classification %s", classification.id)
        except httpx.HTTPError:
            logger.exception("Telegram notification failed for classification %s", classification.id)
            status = "failed"

        return self._repository.create(
            classification_id=classification.id,
            channel="telegram",
            recipient=str(recipient),
            message=message,
            status=status,
        )
