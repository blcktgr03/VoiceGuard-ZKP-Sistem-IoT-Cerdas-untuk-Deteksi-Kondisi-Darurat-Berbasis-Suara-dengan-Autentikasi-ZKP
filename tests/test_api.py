from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint() -> None:
    """Check that the FastAPI app exposes a health endpoint."""
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_contains_core_routes() -> None:
    """Check that Swagger/OpenAPI includes the core system endpoints."""
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/challenge" in paths
    assert "/verify" in paths
    assert "/api/process/audio" in paths


def test_dashboard_and_monitoring_routes_exist() -> None:
    """Check that the dashboard and monitoring JSON endpoints are available."""
    with TestClient(app) as client:
        dashboard = client.get("/dashboard")
        overview = client.get("/api/monitoring/overview")
        events = client.get("/api/monitoring/events")

    assert dashboard.status_code == 200
    assert "Monitoring Dashboard" in dashboard.text
    assert overview.status_code == 200
    assert "total_devices" in overview.json()
    assert events.status_code == 200
    assert isinstance(events.json(), list)
