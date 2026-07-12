from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.audio_record import AudioRecord
from backend.models.classification import Classification
from backend.models.device import Device
from backend.models.notification import Notification
from backend.models.transcript import Transcript


class MonitoringRepository:
    """Read-only queries for dashboard monitoring."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_overview(self) -> dict[str, object]:
        """Return aggregate counters for the dashboard."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        total_devices = self._db.scalar(select(func.count(Device.id))) or 0
        active_devices = self._db.scalar(
            select(func.count(Device.id)).where(Device.status == "active")
        ) or 0
        total_events_24h = self._db.scalar(
            select(func.count(Classification.id)).where(Classification.created_at >= cutoff)
        ) or 0
        emergency_events_24h = self._db.scalar(
            select(func.count(Classification.id)).where(
                Classification.created_at >= cutoff,
                Classification.label == "Emergency",
            )
        ) or 0
        sent_notifications_24h = self._db.scalar(
            select(func.count(Notification.id)).where(
                Notification.created_at >= cutoff,
                Notification.status == "sent",
            )
        ) or 0
        failed_notifications_24h = self._db.scalar(
            select(func.count(Notification.id)).where(
                Notification.created_at >= cutoff,
                Notification.status == "failed",
            )
        ) or 0
        last_event_at = self._db.scalar(
            select(Classification.created_at).order_by(Classification.created_at.desc()).limit(1)
        )

        return {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "total_events_24h": total_events_24h,
            "emergency_events_24h": emergency_events_24h,
            "sent_notifications_24h": sent_notifications_24h,
            "failed_notifications_24h": failed_notifications_24h,
            "last_event_at": last_event_at,
        }

    def list_recent_events(self, limit: int = 12) -> list[dict[str, object]]:
        """Return the latest classified events with device and notification details."""
        limit = max(1, min(limit, 50))
        statement = (
            select(
                Classification.id.label("event_id"),
                Classification.created_at.label("created_at"),
                Device.device_id.label("device_id"),
                Device.name.label("device_name"),
                Device.location.label("device_location"),
                AudioRecord.file_name.label("audio_file_name"),
                Transcript.text.label("transcript_text"),
                Classification.label.label("label"),
                Classification.confidence.label("confidence"),
                Notification.status.label("notification_status"),
                Notification.channel.label("notification_channel"),
                Notification.recipient.label("notification_recipient"),
                Notification.message.label("notification_message"),
            )
            .select_from(Classification)
            .join(Transcript, Classification.transcript_id == Transcript.id)
            .join(AudioRecord, Transcript.audio_record_id == AudioRecord.id)
            .join(Device, AudioRecord.device_id == Device.id)
            .outerjoin(Notification, Notification.classification_id == Classification.id)
            .order_by(Classification.created_at.desc())
            .limit(limit)
        )

        rows = self._db.execute(statement).all()
        return [dict(row._mapping) for row in rows]
