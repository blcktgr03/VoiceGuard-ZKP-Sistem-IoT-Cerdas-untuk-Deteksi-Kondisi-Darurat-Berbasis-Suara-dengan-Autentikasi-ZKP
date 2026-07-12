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


class FakeTextClassificationService:
    """Fake BERT service for unit tests."""

    def classify(self, text: str) -> ClassificationResult:
        """Return a deterministic emergency prediction."""
        return ClassificationResult(
            label=ClassificationLabel.EMERGENCY,
            confidence=0.95,
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
        assert response.classification.confidence == 0.95
        assert response.notification is not None
        assert response.server_proof.public_key
    finally:
        db.close()
        get_settings.cache_clear()
