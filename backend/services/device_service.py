from backend.api.schemas import DeviceCreate
from backend.models.device import Device
from backend.repositories.device_repository import DeviceRepository


class DeviceService:
    """Use-case service for registered IoT devices."""

    def __init__(self, repository: DeviceRepository) -> None:
        """Create the service with a device repository."""
        self._repository = repository

    def create(self, payload: DeviceCreate) -> Device:
        """Register a new device."""
        return self._repository.create(payload)

    def list(self) -> list[Device]:
        """Return all registered devices."""
        return self._repository.list()

    def get_by_device_id(self, device_id: str) -> Device | None:
        """Find one device by its external identifier."""
        return self._repository.get_by_device_id(device_id)
