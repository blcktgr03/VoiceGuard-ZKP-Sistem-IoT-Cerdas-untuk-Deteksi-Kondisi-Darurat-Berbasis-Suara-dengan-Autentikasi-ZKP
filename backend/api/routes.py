from fastapi import APIRouter

from backend.api.v1 import auth, devices, health, monitoring, processing

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(processing.router, prefix="/process", tags=["processing"])
api_router.include_router(monitoring.router, tags=["monitoring"])
