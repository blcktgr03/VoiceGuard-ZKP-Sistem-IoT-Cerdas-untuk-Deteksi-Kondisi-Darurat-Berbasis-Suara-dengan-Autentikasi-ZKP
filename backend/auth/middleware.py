from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.auth.tokens import AuthTokenService


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Require a valid X-Auth-Token header for protected routes."""

    def __init__(
        self,
        app,
        token_service: AuthTokenService,
        protected_prefixes: tuple[str, ...],
    ) -> None:
        """Create middleware for selected URL prefixes."""
        super().__init__(app)
        self._token_service = token_service
        self._protected_prefixes = protected_prefixes

    async def dispatch(self, request: Request, call_next):
        """Validate protected requests before they reach route handlers."""
        if not request.url.path.startswith(self._protected_prefixes):
            return await call_next(request)

        token = request.headers.get("X-Auth-Token")
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing X-Auth-Token header."},
            )

        authenticated = self._token_service.verify(token)
        if authenticated is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired authentication token."},
            )

        request.state.authenticated_device = authenticated
        return await call_next(request)
