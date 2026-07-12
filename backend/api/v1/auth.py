from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_authentication_service
from backend.api.schemas import AuthProofRequest, AuthResultRead, ChallengeRequest, ChallengeResponse
from backend.auth.service import AuthenticationService

router = APIRouter()


@router.post("/challenge", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
def request_challenge(
    payload: ChallengeRequest,
    service: AuthenticationService = Depends(get_authentication_service),
):
    """Create and persist a short-lived Schnorr challenge for a commitment."""
    result = service.request_challenge(payload)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found.")
    return ChallengeResponse(
        device_id=result.device_id,
        challenge=result.challenge,
        expires_at=result.expires_at,
    )


@router.post("/verify", response_model=AuthResultRead, status_code=status.HTTP_200_OK)
def verify_authentication(
    payload: AuthProofRequest,
    service: AuthenticationService = Depends(get_authentication_service),
):
    """Verify a Schnorr response and issue an upload token."""
    result = service.verify_device(payload)
    return AuthResultRead(
        authenticated=result.authenticated,
        reason=result.reason,
        auth_token=result.auth_token,
    )
