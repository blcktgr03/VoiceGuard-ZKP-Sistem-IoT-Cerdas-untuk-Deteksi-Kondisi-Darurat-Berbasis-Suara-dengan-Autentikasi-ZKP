from backend.config.settings import Settings


def ensure_runtime_directories(settings: Settings) -> None:
    """Create runtime folders used by uploads and logs."""
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
