from types import SimpleNamespace

from backend.api.schemas import ClassificationLabel
from backend.bert.service import ClassificationResult
from backend.services.classification_service import ClassificationService
from backend.services.emergency_service import EmergencyProcessingService


class AlwaysNormalClassifier:
    def classify(self, text: str) -> ClassificationResult:
        return ClassificationResult(
            label=ClassificationLabel.NORMAL,
            confidence=0.75,
            model_name="fake-indobert",
        )


class CaptureClassificationRepository:
    def create(self, **values):
        return SimpleNamespace(**values)


def test_keyword_rule_overrides_normal_bert_result() -> None:
    service = ClassificationService(
        CaptureClassificationRepository(),
        AlwaysNormalClassifier(),
    )

    result = service.classify_and_save(
        transcript_id=1,
        text="Tolong kebakaran",
        force_emergency=True,
    )

    assert result.label == ClassificationLabel.EMERGENCY
    assert result.confidence >= 0.85
    assert result.model_name.endswith("+indonesian-keyword-rule")


def test_negation_blocks_keyword_emergency_detection() -> None:
    service = object.__new__(EmergencyProcessingService)

    assert service._looks_like_emergency_transcript(["tolong"]) is True
    assert service._looks_like_emergency_transcript(
        ["bukan", "keadaan", "darurat"]
    ) is False
    assert service._looks_like_emergency_transcript(["semua", "aman"]) is False
    assert service._looks_like_emergency_transcript(["saya", "tidak", "sakit"]) is False
    assert service._looks_like_emergency_transcript(
        ["tidak", "ada", "kebakaran"]
    ) is False
