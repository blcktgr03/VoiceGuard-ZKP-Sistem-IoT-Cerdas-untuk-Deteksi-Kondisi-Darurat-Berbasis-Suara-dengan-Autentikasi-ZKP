from sqlalchemy.orm import Session

from backend.api.schemas import ClassificationLabel
from backend.models.audio_record import AudioRecord
from backend.models.classification import Classification
from backend.models.transcript import Transcript


class ClassificationRepository:
    """Persist BERT classification rows."""

    def __init__(self, db: Session) -> None:
        """Create a repository with an active database session."""
        self._db = db

    def create(
        self,
        transcript_id: int,
        label: ClassificationLabel,
        confidence: float,
        model_name: str,
    ) -> Classification:
        """Insert a classification row."""
        classification = Classification(
            transcript_id=transcript_id,
            label=label.value,
            confidence=confidence,
            model_name=model_name,
        )
        self._db.add(classification)
        self._db.commit()
        self._db.refresh(classification)
        return classification

    def get_previous_for_device(
        self,
        device_id: int,
        current_classification_id: int,
    ) -> Classification | None:
        """Return the previous classification for the same device."""
        return (
            self._db.query(Classification)
            .join(Transcript, Classification.transcript_id == Transcript.id)
            .join(AudioRecord, Transcript.audio_record_id == AudioRecord.id)
            .filter(AudioRecord.device_id == device_id)
            .filter(Classification.id != current_classification_id)
            .order_by(Classification.created_at.desc(), Classification.id.desc())
            .first()
        )
