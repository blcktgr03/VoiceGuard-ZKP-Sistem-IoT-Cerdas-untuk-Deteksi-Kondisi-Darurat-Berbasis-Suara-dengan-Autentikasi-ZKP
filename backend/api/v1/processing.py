from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from starlette.datastructures import Headers

from backend.api.dependencies import get_emergency_processing_service
from backend.api.schemas import PresentEncryptedAudioRequest, ProcessingResponse
from backend.crypto.present128 import PresentCipherError, decrypt_audio_payload
from backend.services.emergency_service import EmergencyProcessingService

router = APIRouter()


@router.post("/audio", response_model=ProcessingResponse, status_code=status.HTTP_201_CREATED)
def process_audio(
    request: Request,
    device_id: str = Form(...),
    audio_file: UploadFile = File(...),
    service: EmergencyProcessingService = Depends(get_emergency_processing_service),
):
    """Process an authenticated audio upload through Whisper, BERT, Telegram, and server proof."""
    authenticated = getattr(request.state, "authenticated_device", None)
    if authenticated is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated request.")
    if authenticated.device_id != device_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token device does not match submitted device ID.",
        )

    return service.process_audio(
        device_db_id=authenticated.device_db_id,
        device_id=authenticated.device_id,
        audio_file=audio_file,
    )


@router.post("/audio/present128", response_model=ProcessingResponse, status_code=status.HTTP_201_CREATED)
def process_present128_audio(
    request: Request,
    encrypted_audio: PresentEncryptedAudioRequest,
    service: EmergencyProcessingService = Depends(get_emergency_processing_service),
):
    """Decrypt a PRESENT-128 payload, then process the recovered audio through the existing ML pipeline."""
    authenticated = getattr(request.state, "authenticated_device", None)
    if authenticated is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated request.")
    if authenticated.device_id != encrypted_audio.device_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token device does not match submitted device ID.",
        )

    try:
        audio_bytes = decrypt_audio_payload(
            device_id=authenticated.device_id,
            nonce_hex=encrypted_audio.nonce_hex,
            ciphertext_b64=encrypted_audio.ciphertext_b64,
            tag_hex=encrypted_audio.tag_hex,
            filename=encrypted_audio.filename,
            mime_type=encrypted_audio.mime_type,
        )
    except PresentCipherError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    audio_file = UploadFile(
        filename=encrypted_audio.filename,
        file=BytesIO(audio_bytes),
        headers=Headers({"content-type": encrypted_audio.mime_type}),
    )
    return service.process_audio(
        device_db_id=authenticated.device_db_id,
        device_id=authenticated.device_id,
        audio_file=audio_file,
    )
