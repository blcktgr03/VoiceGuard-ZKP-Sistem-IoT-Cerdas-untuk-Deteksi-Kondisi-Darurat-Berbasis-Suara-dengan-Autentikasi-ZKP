from backend.bert.service import TextClassificationService
from backend.config.settings import get_settings
from backend.models.classification import Classification
from backend.repositories.classification_repository import ClassificationRepository


class ClassificationService:
    """Classify transcripts and apply the emergency threshold policy."""

    def __init__(
        self,
        repository: ClassificationRepository,
        classifier: TextClassificationService,
    ) -> None:
        """Create a classification coordinator."""
        self._repository = repository
        self._classifier = classifier
        self._settings = get_settings()

    def classify_and_save(self, transcript_id: int, text: str) -> Classification:
        """Classify transcript text and persist the result."""
        result = self._classifier.classify(text)
        return self._repository.create(
            transcript_id=transcript_id,
            label=result.label,
            confidence=result.confidence,
            model_name=result.model_name,
        )

    def is_emergency(self, classification: Classification) -> bool:
        """Return true when a classification should trigger emergency handling."""
        return (
            classification.label == "Emergency"
            and classification.confidence >= self._settings.emergency_threshold
        )
