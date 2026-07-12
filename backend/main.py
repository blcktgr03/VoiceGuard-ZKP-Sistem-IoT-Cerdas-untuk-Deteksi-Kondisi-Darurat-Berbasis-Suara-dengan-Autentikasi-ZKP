from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import api_router
from backend.api.v1 import auth
from backend.auth.middleware import AuthenticationMiddleware
from backend.auth.tokens import AuthTokenService
from backend.config.settings import get_settings
from backend.database.session import create_database
from backend.utils.exception_handlers import app_error_handler, unhandled_exception_handler
from backend.utils.exceptions import AppError
from backend.utils.files import ensure_runtime_directories
from backend.utils.logging import configure_logging
from backend.api.v1.monitoring import dashboard as monitoring_dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare runtime directories, logging, and database tables."""
    settings = get_settings()
    ensure_runtime_directories(settings)
    configure_logging(settings)
    create_database()
    yield


app = FastAPI(
    title="Secure Voice-Based Emergency Detection System",
    description=(
        "IoT emergency detection backend using ESP8266 authentication, "
        "Schnorr ZKP, Whisper speech-to-text, BERT classification, "
        "Telegram notification, and server proof verification."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "health", "description": "Runtime health checks."},
        {"name": "devices", "description": "Device registration and lookup."},
        {"name": "authentication", "description": "Schnorr challenge-response authentication."},
        {"name": "processing", "description": "Authenticated audio upload and ML processing."},
        {"name": "monitoring", "description": "Live dashboard data for device and emergency monitoring."},
    ],
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    AuthenticationMiddleware,
    token_service=AuthTokenService(settings.auth_token_secret, settings.auth_token_ttl_seconds),
    protected_prefixes=("/api/process", "/process"),
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(api_router)
app.include_router(auth.router)
app.add_api_route("/dashboard", monitoring_dashboard, methods=["GET"], include_in_schema=False)
