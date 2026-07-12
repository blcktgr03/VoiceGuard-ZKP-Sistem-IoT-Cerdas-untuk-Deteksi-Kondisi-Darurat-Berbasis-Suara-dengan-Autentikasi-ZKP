from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api.schemas import DeviceCreate
from backend.models.device import Device


class DeviceRepository:
    """Persist and query registered devices."""

    def __init__(self, db: Session) -> None:
        """Create a repository with an active database session."""
        self._db = db

    def create(self, payload: DeviceCreate) -> Device:
        """Insert a new device row."""
        device = Device(**payload.model_dump())
        self._db.add(device)
        self._db.commit()
        self._db.refresh(device)
        return device

    def list(self) -> list[Device]:
        """Return devices ordered by newest first."""
        return list(self._db.scalars(select(Device).order_by(Device.created_at.desc())))

    def get_by_device_id(self, device_id: str) -> Device | None:
        """Find a device by its external device ID."""
        statement = select(Device).where(Device.device_id == device_id)
        return self._db.scalar(statement)
