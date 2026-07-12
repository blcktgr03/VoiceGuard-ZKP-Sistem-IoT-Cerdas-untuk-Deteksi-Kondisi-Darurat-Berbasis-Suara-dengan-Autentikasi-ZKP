from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_device_service
from backend.api.schemas import DeviceCreate, DeviceRead
from backend.services.device_service import DeviceService

router = APIRouter()


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(
    payload: DeviceCreate,
    service: DeviceService = Depends(get_device_service),
):
    """Register a device and its Schnorr public key."""
    existing = service.get_by_device_id(payload.device_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device ID already exists.",
        )
    return service.create(payload)


@router.get("", response_model=list[DeviceRead])
def list_devices(service: DeviceService = Depends(get_device_service)):
    """List registered devices."""
    return service.list()


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: str, service: DeviceService = Depends(get_device_service)):
    """Return one registered device by external device ID."""
    device = service.get_by_device_id(device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found.")
    return device
