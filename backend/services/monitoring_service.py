from backend.api.schemas import MonitoringEventRead, MonitoringOverviewRead
from backend.repositories.monitoring_repository import MonitoringRepository


class MonitoringService:
    """Compose read-only monitoring data for the dashboard."""

    def __init__(self, repository: MonitoringRepository) -> None:
        self._repository = repository

    def get_overview(self) -> MonitoringOverviewRead:
        """Return dashboard summary metrics."""
        return MonitoringOverviewRead.model_validate(self._repository.get_overview())

    def list_recent_events(self, limit: int = 12) -> list[MonitoringEventRead]:
        """Return latest monitoring events."""
        return [
            MonitoringEventRead.model_validate(row)
            for row in self._repository.list_recent_events(limit=limit)
        ]
