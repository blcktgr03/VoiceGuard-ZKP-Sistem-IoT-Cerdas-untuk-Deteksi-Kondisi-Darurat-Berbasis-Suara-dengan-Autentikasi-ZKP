from datetime import datetime
try:
    from enum import StrEnum
except ImportError:  # Python 3.10 compatibility for the training environment.
    from enum import Enum

    class StrEnum(str, Enum):
        pass

from pydantic import BaseModel, ConfigDict, Field


class DeviceStatus(StrEnum):
    """Supported lifecycle states for a registered device."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class ClassificationLabel(StrEnum):
    """Labels returned by the emergency classifier."""

    EMERGENCY = "Emergency"
    NORMAL = "Normal"
    UNKNOWN = "Unknown"


class DeviceCreate(BaseModel):
    """Request body for device registration."""

    device_id: str = Field(min_length=3, max_length=80)
    name: str = Field(min_length=1, max_length=120)
    public_key: str = Field(min_length=1)
    location: str | None = Field(default=None, max_length=255)


class DeviceRead(BaseModel):
    """Response body for registered device data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    name: str
    public_key: str
    location: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class AuthProofRequest(BaseModel):
    """Request body for Schnorr proof verification."""

    device_id: str
    commitment: str
    response: str


class AuthResultRead(BaseModel):
    """Response body for authentication verification."""

    authenticated: bool
    reason: str
    auth_token: str | None = None


class ChallengeRequest(BaseModel):
    """Request body for Schnorr challenge generation."""

    device_id: str
    commitment: str


class ChallengeResponse(BaseModel):
    """Response body containing the generated challenge."""

    device_id: str
    challenge: int
    expires_at: datetime


class ServerProofRead(BaseModel):
    """Server proof returned with classification results."""

    public_key: str
    commitment: str
    challenge: str
    response: str
    message: str


class AudioRecordRead(BaseModel):
    """Response body for uploaded audio metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    file_name: str
    file_path: str
    mime_type: str | None
    size_bytes: int
    created_at: datetime


class TranscriptRead(BaseModel):
    """Response body for Whisper transcript data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    audio_record_id: int
    text: str
    engine: str
    created_at: datetime


class ClassificationRead(BaseModel):
    """Response body for BERT classification output."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    transcript_id: int
    label: ClassificationLabel
    confidence: float
    model_name: str
    created_at: datetime


class NotificationRead(BaseModel):
    """Response body for Telegram notification status."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    classification_id: int
    channel: str
    recipient: str
    message: str
    status: str
    created_at: datetime


class ProcessingResponse(BaseModel):
    """Full response body for the end-to-end audio processing endpoint."""

    authenticated: bool
    emergency_detected: bool
    audio: AudioRecordRead
    transcript: TranscriptRead
    classification: ClassificationRead
    notification: NotificationRead | None = None
    server_proof: ServerProofRead


class PresentEncryptedAudioRequest(BaseModel):
    """JSON body for PRESENT-128 encrypted audio uploads."""

    device_id: str = Field(min_length=3, max_length=80)
    nonce_hex: str = Field(min_length=16, max_length=16)
    ciphertext_b64: str = Field(min_length=1)
    tag_hex: str = Field(min_length=64, max_length=64)
    filename: str = Field(default="chunk.wav", min_length=1, max_length=120)
    mime_type: str = Field(default="audio/wav", min_length=1, max_length=120)


class MonitoringOverviewRead(BaseModel):
    """High-level summary values for the dashboard."""

    total_devices: int
    active_devices: int
    total_events_24h: int
    emergency_events_24h: int
    sent_notifications_24h: int
    failed_notifications_24h: int
    last_event_at: datetime | None = None


class MonitoringEventRead(BaseModel):
    """Single row displayed in the live monitoring feed."""

    event_id: int
    created_at: datetime
    device_id: str
    device_name: str
    device_location: str | None
    audio_file_name: str
    transcript_text: str
    label: ClassificationLabel
    confidence: float
    notification_status: str | None = None
    notification_channel: str | None = None
    notification_recipient: str | None = None
    notification_message: str | None = None
