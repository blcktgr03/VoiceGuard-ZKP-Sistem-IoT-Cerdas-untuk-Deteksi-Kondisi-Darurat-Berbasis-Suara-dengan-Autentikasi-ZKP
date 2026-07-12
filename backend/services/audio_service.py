from pathlib import Path
from uuid import uuid4
import logging

from fastapi import UploadFile

from backend.config.settings import get_settings
from backend.models.audio_record import AudioRecord
from backend.repositories.audio_repository import AudioRepository
from backend.utils.exceptions import AudioProcessingError

logger = logging.getLogger(__name__)


class AudioService:
    """Store uploaded audio and persist its metadata."""

    def __init__(self, repository: AudioRepository) -> None:
        """Create an audio service backed by an audio repository."""
        self._repository = repository
        self._settings = get_settings()

    def save_upload(self, device_db_id: int, audio_file: UploadFile) -> AudioRecord:
        """Save an uploaded audio file and create an AudioRecord row."""
        if not audio_file.filename:
            raise AudioProcessingError("Uploaded audio must include a filename.")

        suffix = Path(audio_file.filename or "audio.bin").suffix
        safe_name = f"{uuid4().hex}{suffix or '.bin'}"
        target_path = self._settings.upload_dir / safe_name

        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = audio_file.file.read()
        if not content:
            raise AudioProcessingError("Uploaded audio file is empty.")

        target_path.write_bytes(content)
        audio_file.file.seek(0)
        logger.info("Saved uploaded audio to %s (%s bytes)", target_path, len(content))

        return self._repository.create(
            device_id=device_db_id,
            file_name=audio_file.filename or safe_name,
            file_path=str(target_path),
            mime_type=audio_file.content_type,
            size_bytes=len(content),
        )
