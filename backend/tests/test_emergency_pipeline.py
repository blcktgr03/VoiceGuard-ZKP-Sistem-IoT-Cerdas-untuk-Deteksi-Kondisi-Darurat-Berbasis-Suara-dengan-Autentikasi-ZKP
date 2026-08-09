from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.api.schemas import ClassificationLabel
from backend.bert.service import ClassificationResult
from backend.config.settings import get_settings
from backend.database.base import Base
from backend.models import all_models  # noqa: F401
from backend.models.classification import Classification
from backend.repositories.audio_repository import AudioRepository
from backend.repositories.classification_repository import ClassificationRepository
from backend.repositories.notification_repository import NotificationRepository
from backend.repositories.transcript_repository import TranscriptRepository
from backend.services.audio_service import AudioService
from backend.services.classification_service import ClassificationService
from backend.services.emergency_service import EmergencyProcessingService
from backend.telegram.service import NotificationService
from backend.zkp.service import ZkpService


class FakeSpeechToTextService:
    """Fake Whisper service for unit tests."""

    def transcribe(self, file_path: str) -> str:
        """Return a deterministic emergency transcript."""
        assert Path(file_path).exists()
        return "Help, there is a fire in the work area."


class RepetitiveSpeechToTextService:
    """Fake Whisper service that mimics noisy repeated hallucination output."""

    def transcribe(self, file_path: str) -> str:
        """Return a repeated transcript like weak microphone audio can produce."""
        assert Path(file_path).exists()
        return "kepakannya di tempat di tempat di tempat di tempat di tempat di tempat"


class FakeTextClassificationService:
    """Fake BERT service for unit tests."""

    def classify(self, text: str) -> ClassificationResult:
        """Return a deterministic emergency prediction."""
        return ClassificationResult(
            label=ClassificationLabel.EMERGENCY,
            confidence=0.95,
            model_name="fake-bert",
        )


class SequenceTextClassificationService:
    """Fake BERT service that returns confidence values in order."""

    def __init__(self, confidences: list[float]) -> None:
        self._confidences = confidences
        self._index = 0

    def classify(self, text: str) -> ClassificationResult:
        confidence = self._confidences[self._index]
        self._index += 1
        return ClassificationResult(
            label=ClassificationLabel.EMERGENCY,
            confidence=confidence,
            model_name="fake-bert",
        )


class TextAwareClassificationService:
    """Fake BERT service that marks no-speech text as Normal."""

    def classify(self, text: str) -> ClassificationResult:
        label = (
            ClassificationLabel.NORMAL
            if "tidak ada suara terdeteksi" in text
            else ClassificationLabel.EMERGENCY
        )
        confidence = 0.99 if label == ClassificationLabel.NORMAL else 0.95
        return ClassificationResult(
            label=label,
            confidence=confidence,
            model_name="fake-bert",
        )


class FakeNotificationService(NotificationService):
    """Fake Telegram service that records a notification without network calls."""

    def send_emergency_alert(self, classification: Classification, message: str):
        """Persist a sent notification without calling Telegram."""
        return self._repository.create(
            classification_id=classification.id,
            channel="telegram",
            recipient="test-chat",
            message=message,
            status="sent",
        )


def test_emergency_pipeline_persists_outputs(tmp_path, monkeypatch) -> None:
    """Run the ML pipeline with fake ML services and verify persisted outputs."""
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("WHISPER_MODEL_NAME", "fake-whisper")
    monkeypatch.setenv("EMERGENCY_THRESHOLD", "0.8")
    get_settings.cache_clear()

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, class_=Session)
    db = session_factory()

    try:
        audio_repository = AudioRepository(db)
        transcript_repository = TranscriptRepository(db)
        classification_repository = ClassificationRepository(db)
        notification_repository = NotificationRepository(db)

        service = EmergencyProcessingService(
            audio_service=AudioService(audio_repository),
            transcript_repository=transcript_repository,
            speech_to_text_service=FakeSpeechToTextService(),
            classification_service=ClassificationService(
                classification_repository,
                FakeTextClassificationService(),
            ),
            notification_service=FakeNotificationService(notification_repository),
            zkp_service=ZkpService(),
        )

        audio_path = tmp_path / "sample.raw"
        audio_path.write_bytes(b"audio-bytes")
        with audio_path.open("rb") as file_obj:
            upload = UploadFile(file=file_obj, filename="sample.raw")
            response = service.process_audio(
                device_db_id=1,
                device_id="esp8266-worker-01",
                audio_file=upload,
            )

        assert response.transcript.text == "Help, there is a fire in the work area."
        assert response.classification.label == ClassificationLabel.EMERGENCY
        assert response.emergency_detected is True
        assert response.classification.confidence == 0.95
        assert response.notification is not None
        assert response.server_proof.public_key
    finally:
        db.close()
        get_settings.cache_clear()


def test_emergency_policy_requires_high_confidence_or_two_consecutive_chunks(
    tmp_path,
    monkeypatch,
) -> None:
    """Trigger alerts for one high-confidence chunk or two medium-confidence chunks."""
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("WHISPER_MODEL_NAME", "fake-whisper")
    monkeypatch.setenv("EMERGENCY_THRESHOLD", "0.7")
    monkeypatch.setenv("EMERGENCY_HIGH_CONFIDENCE_THRESHOLD", "0.85")
    get_settings.cache_clear()

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, class_=Session)
    db = session_factory()

    try:
        audio_repository = AudioRepository(db)
        transcript_repository = TranscriptRepository(db)
        classification_repository = ClassificationRepository(db)
        notification_repository = NotificationRepository(db)

        service = EmergencyProcessingService(
            audio_service=AudioService(audio_repository),
            transcript_repository=transcript_repository,
            speech_to_text_service=FakeSpeechToTextService(),
            classification_service=ClassificationService(
                classification_repository,
                SequenceTextClassificationService([0.75, 0.75, 0.95]),
            ),
            notification_service=FakeNotificationService(notification_repository),
            zkp_service=ZkpService(),
        )

        audio_path = tmp_path / "sample.raw"
        audio_path.write_bytes(b"audio-bytes")

        with audio_path.open("rb") as file_obj:
            first = service.process_audio(
                device_db_id=1,
                device_id="esp8266-worker-01",
                audio_file=UploadFile(file=file_obj, filename="first.raw"),
            )
        with audio_path.open("rb") as file_obj:
            second = service.process_audio(
                device_db_id=1,
                device_id="esp8266-worker-01",
                audio_file=UploadFile(file=file_obj, filename="second.raw"),
            )
        with audio_path.open("rb") as file_obj:
            third = service.process_audio(
                device_db_id=2,
                device_id="esp8266-worker-02",
                audio_file=UploadFile(file=file_obj, filename="third.raw"),
            )

        assert first.notification is None
        assert second.notification is not None
        assert third.notification is not None
    finally:
        db.close()
        get_settings.cache_clear()


def test_repetitive_whisper_hallucination_is_not_classified_as_emergency(
    tmp_path,
    monkeypatch,
) -> None:
    """Repeated low-quality STT output is stored for review but classified as no speech."""
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("WHISPER_MODEL_NAME", "fake-whisper")
    monkeypatch.setenv("EMERGENCY_THRESHOLD", "0.7")
    get_settings.cache_clear()

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, class_=Session)
    db = session_factory()

    try:
        audio_repository = AudioRepository(db)
        transcript_repository = TranscriptRepository(db)
        classification_repository = ClassificationRepository(db)
        notification_repository = NotificationRepository(db)

        service = EmergencyProcessingService(
            audio_service=AudioService(audio_repository),
            transcript_repository=transcript_repository,
            speech_to_text_service=RepetitiveSpeechToTextService(),
            classification_service=ClassificationService(
                classification_repository,
                TextAwareClassificationService(),
            ),
            notification_service=FakeNotificationService(notification_repository),
            zkp_service=ZkpService(),
        )

        audio_path = tmp_path / "sample.raw"
        audio_path.write_bytes(b"audio-bytes")
        with audio_path.open("rb") as file_obj:
            response = service.process_audio(
                device_db_id=1,
                device_id="esp8266-worker-01",
                audio_file=UploadFile(file=file_obj, filename="sample.raw"),
            )

        assert response.transcript.text.startswith("tidak ada suara terdeteksi")
        assert "transkrip tidak valid" in response.transcript.text
        assert response.classification.label == ClassificationLabel.NORMAL
        assert response.notification is None
    finally:
        db.close()
        get_settings.cache_clear()
