from sqlalchemy.orm import Session

from backend.api.schemas import ClassificationLabel
from backend.models.classification import Classification


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
