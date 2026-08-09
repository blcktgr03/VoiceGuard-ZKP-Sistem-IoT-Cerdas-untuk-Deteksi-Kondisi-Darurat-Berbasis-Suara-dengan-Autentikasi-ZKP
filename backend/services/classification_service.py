from backend.bert.service import TextClassificationService
from backend.api.schemas import ClassificationLabel
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

    def classify_and_save(
        self,
        transcript_id: int,
        text: str,
        force_emergency: bool = False,
    ) -> Classification:
        """Classify transcript text and persist the result."""
        result = self._classifier.classify(text)
        label = result.label
        confidence = result.confidence
        model_name = result.model_name
        if force_emergency:
            label = ClassificationLabel.EMERGENCY
            confidence = max(confidence, self._settings.emergency_high_confidence_threshold)
            model_name = f"{model_name}+indonesian-keyword-rule"

        return self._repository.create(
            transcript_id=transcript_id,
            label=label,
            confidence=confidence,
            model_name=model_name,
        )

    def should_trigger_emergency(self, device_db_id: int, classification: Classification) -> bool:
        """Apply chunk-based emergency notification policy for one device."""
        if classification.label != "Emergency":
            return False

        if classification.confidence >= self._settings.emergency_high_confidence_threshold:
            return True

        if classification.confidence < self._settings.emergency_threshold:
            return False

        previous = self._repository.get_previous_for_device(
            device_id=device_db_id,
            current_classification_id=classification.id,
        )
        return (
            previous is not None
            and previous.label == "Emergency"
            and previous.confidence >= self._settings.emergency_threshold
        )
