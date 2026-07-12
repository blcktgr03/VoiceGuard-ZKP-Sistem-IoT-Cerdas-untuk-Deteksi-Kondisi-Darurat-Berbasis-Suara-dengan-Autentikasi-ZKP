from sqlalchemy.orm import Session

from backend.models.audio_record import AudioRecord


class AudioRepository:
    """Persist uploaded audio metadata."""

    def __init__(self, db: Session) -> None:
        """Create a repository with an active database session."""
        self._db = db

    def create(
        self,
        device_id: int,
        file_name: str,
        file_path: str,
        mime_type: str | None,
        size_bytes: int,
    ) -> AudioRecord:
        """Insert an audio record row."""
        record = AudioRecord(
            device_id=device_id,
            file_name=file_name,
            file_path=file_path,
            mime_type=mime_type,
            size_bytes=size_bytes,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record
