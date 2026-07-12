from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from backend.api.dependencies import get_emergency_processing_service
from backend.api.schemas import ProcessingResponse
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
