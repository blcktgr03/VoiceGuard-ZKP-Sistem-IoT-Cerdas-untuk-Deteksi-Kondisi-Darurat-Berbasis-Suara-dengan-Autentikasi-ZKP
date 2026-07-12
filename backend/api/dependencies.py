from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.auth.service import AuthenticationService
from backend.auth.tokens import AuthTokenService
from backend.bert.service import TextClassificationService
from backend.config.settings import get_settings
from backend.database.session import get_db
from backend.repositories.audio_repository import AudioRepository
from backend.repositories.auth_repository import AuthenticationLogRepository
from backend.repositories.challenge_repository import AuthenticationChallengeRepository
from backend.repositories.classification_repository import ClassificationRepository
from backend.repositories.device_repository import DeviceRepository
from backend.repositories.monitoring_repository import MonitoringRepository
from backend.repositories.notification_repository import NotificationRepository
from backend.repositories.transcript_repository import TranscriptRepository
from backend.services.audio_service import AudioService
from backend.services.classification_service import ClassificationService
from backend.services.device_service import DeviceService
from backend.services.emergency_service import EmergencyProcessingService
from backend.services.monitoring_service import MonitoringService
from backend.speech.service import SpeechToTextService
from backend.telegram.service import NotificationService
from backend.zkp.service import ZkpService


def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_device_repository(db: Session = Depends(db_session)) -> DeviceRepository:
    return DeviceRepository(db)


def get_auth_log_repository(db: Session = Depends(db_session)) -> AuthenticationLogRepository:
    return AuthenticationLogRepository(db)


def get_challenge_repository(db: Session = Depends(db_session)) -> AuthenticationChallengeRepository:
    return AuthenticationChallengeRepository(db)


def get_audio_repository(db: Session = Depends(db_session)) -> AudioRepository:
    return AudioRepository(db)


def get_transcript_repository(db: Session = Depends(db_session)) -> TranscriptRepository:
    return TranscriptRepository(db)


def get_classification_repository(db: Session = Depends(db_session)) -> ClassificationRepository:
    return ClassificationRepository(db)


def get_notification_repository(db: Session = Depends(db_session)) -> NotificationRepository:
    return NotificationRepository(db)


def get_monitoring_repository(db: Session = Depends(db_session)) -> MonitoringRepository:
    return MonitoringRepository(db)


@lru_cache
def get_zkp_service() -> ZkpService:
    return ZkpService()


@lru_cache
def get_auth_token_service() -> AuthTokenService:
    settings = get_settings()
    return AuthTokenService(settings.auth_token_secret, settings.auth_token_ttl_seconds)


@lru_cache
def get_speech_to_text_service() -> SpeechToTextService:
    return SpeechToTextService()


@lru_cache
def get_text_classification_service() -> TextClassificationService:
    return TextClassificationService()


def get_notification_service(
    repository: NotificationRepository = Depends(get_notification_repository),
) -> NotificationService:
    return NotificationService(repository)


def get_classification_service(
    repository: ClassificationRepository = Depends(get_classification_repository),
    classifier: TextClassificationService = Depends(get_text_classification_service),
) -> ClassificationService:
    return ClassificationService(repository, classifier)


def get_device_service(
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceService:
    return DeviceService(repository)


def get_authentication_service(
    devices: DeviceRepository = Depends(get_device_repository),
    challenges: AuthenticationChallengeRepository = Depends(get_challenge_repository),
    logs: AuthenticationLogRepository = Depends(get_auth_log_repository),
    zkp: ZkpService = Depends(get_zkp_service),
    tokens: AuthTokenService = Depends(get_auth_token_service),
) -> AuthenticationService:
    return AuthenticationService(devices, challenges, logs, zkp, tokens)


def get_audio_service(
    repository: AudioRepository = Depends(get_audio_repository),
) -> AudioService:
    return AudioService(repository)


def get_emergency_processing_service(
    audio: AudioService = Depends(get_audio_service),
    transcripts: TranscriptRepository = Depends(get_transcript_repository),
    speech_to_text: SpeechToTextService = Depends(get_speech_to_text_service),
    classifications: ClassificationService = Depends(get_classification_service),
    notifications: NotificationService = Depends(get_notification_service),
    zkp: ZkpService = Depends(get_zkp_service),
) -> EmergencyProcessingService:
    return EmergencyProcessingService(
        audio_service=audio,
        transcript_repository=transcripts,
        speech_to_text_service=speech_to_text,
        classification_service=classifications,
        notification_service=notifications,
        zkp_service=zkp,
    )


def get_monitoring_service(
    repository: MonitoringRepository = Depends(get_monitoring_repository),
) -> MonitoringService:
    return MonitoringService(repository)
