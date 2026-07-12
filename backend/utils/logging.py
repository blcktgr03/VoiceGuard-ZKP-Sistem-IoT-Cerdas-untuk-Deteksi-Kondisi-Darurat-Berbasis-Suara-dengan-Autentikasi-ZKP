import logging
from logging.config import dictConfig

from backend.config.settings import Settings


def configure_logging(settings: Settings) -> None:
    """Configure console and file logging for the application."""
    log_file = settings.log_dir / "app.log"
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": "INFO",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "filename": str(log_file),
                    "level": "INFO",
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": "INFO",
            },
        }
    )
    logging.getLogger(__name__).info("Logging configured.")
