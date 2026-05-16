from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import Settings, get_settings
from app.core.security import extract_bearer_token, validate_token


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Validate JWT on protected routes and attach user context to request.state."""

    def __init__(self, app, settings: Settings | None = None):
        super().__init__(app)
        self.settings = settings or get_settings()

    def _is_public(self, path: str) -> bool:
        return any(
            path == public or path.startswith(f"{public}/")
            for public in self.settings.public_paths
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "OPTIONS" or self._is_public(request.url.path):
            return await call_next(request)

        token = extract_bearer_token(request.headers.get("Authorization"))
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authentication token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = validate_token(token)
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user_id = payload["sub"]
        request.state.user_role = payload.get("role")

        return await call_next(request)
