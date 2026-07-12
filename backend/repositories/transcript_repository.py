from sqlalchemy.orm import Session

from backend.models.transcript import Transcript


class TranscriptRepository:
    """Persist Whisper transcript rows."""

    def __init__(self, db: Session) -> None:
        """Create a repository with an active database session."""
        self._db = db

    def create(self, audio_record_id: int, text: str, engine: str) -> Transcript:
        """Insert a transcript row."""
        transcript = Transcript(audio_record_id=audio_record_id, text=text, engine=engine)
        self._db.add(transcript)
        self._db.commit()
        self._db.refresh(transcript)
        return transcript
