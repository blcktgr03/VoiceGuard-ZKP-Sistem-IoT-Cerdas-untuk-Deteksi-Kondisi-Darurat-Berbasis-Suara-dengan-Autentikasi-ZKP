from dataclasses import dataclass
import logging

from backend.api.schemas import ClassificationLabel
from backend.config.settings import get_settings
from backend.utils.exceptions import ClassificationError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClassificationResult:
    label: ClassificationLabel
    confidence: float
    model_name: str


class TextClassificationService:
    """Classify emergency text with a HuggingFace sequence classification model."""

    def __init__(self) -> None:
        """Create a lazy-loading BERT classification service."""
        self._settings = get_settings()
        self._tokenizer = None
        self._model = None

    def classify(self, text: str) -> ClassificationResult:
        """Return the predicted label and confidence for transcript text."""
        if not text.strip():
            raise ClassificationError("Cannot classify empty text.")

        try:
            tokenizer, model, torch = self._get_components()
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512,
            )
            device = self._torch_device(torch)
            inputs = {key: value.to(device) for key, value in inputs.items()}

            logger.info("Running BERT classification.")
            with torch.no_grad():
                outputs = model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)[0]
                confidence, predicted_index = torch.max(probabilities, dim=0)

            label = self._resolve_label(model, int(predicted_index.item()))
            return ClassificationResult(
                label=self._map_label(label),
                confidence=float(confidence.item()),
                model_name=self._settings.bert_model_name,
            )
        except ClassificationError:
            raise
        except Exception as exc:
            logger.exception("BERT classification failed.")
            raise ClassificationError() from exc

    def _get_components(self):
        """Load and cache tokenizer, model, and torch."""
        if self._tokenizer is None or self._model is None:
            try:
                import torch
                from transformers import AutoModelForSequenceClassification, AutoTokenizer

                logger.info("Loading BERT model '%s'", self._settings.bert_model_name)
                self._tokenizer = AutoTokenizer.from_pretrained(self._settings.bert_model_name)
                self._model = AutoModelForSequenceClassification.from_pretrained(
                    self._settings.bert_model_name
                )
                self._model.to(self._torch_device(torch))
                self._model.eval()
            except Exception as exc:
                logger.exception("Failed to load BERT model.")
                raise ClassificationError() from exc

        import torch

        return self._tokenizer, self._model, torch

    def _torch_device(self, torch):
        """Resolve the configured PyTorch device."""
        if self._settings.bert_device == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    def _resolve_label(self, model, predicted_index: int) -> str:
        """Map a predicted class index to the model label string."""
        id2label = getattr(model.config, "id2label", {}) or {}
        return str(id2label.get(predicted_index, f"LABEL_{predicted_index}"))

    def _map_label(self, label: str) -> ClassificationLabel:
        """Normalize model labels into the API classification enum."""
        normalized = label.strip().lower()
        emergency_labels = self._split_labels(self._settings.bert_emergency_labels)
        normal_labels = self._split_labels(self._settings.bert_normal_labels)

        if normalized in emergency_labels:
            return ClassificationLabel.EMERGENCY
        if normalized in normal_labels:
            return ClassificationLabel.NORMAL

        logger.warning("Unknown BERT label '%s'. Returning Unknown.", label)
        return ClassificationLabel.UNKNOWN

    def _split_labels(self, labels: str) -> set[str]:
        """Split a comma-separated label configuration into normalized labels."""
        return {label.strip().lower() for label in labels.split(",") if label.strip()}
