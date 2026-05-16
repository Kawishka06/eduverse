class FalServiceError(Exception):
    """Base error for the fal.ai integration service."""


class FalResponseParseError(FalServiceError):
    """Raised when a fal.ai response cannot be parsed."""


class FalRequestError(FalServiceError):
    """Raised when a fal.ai API request fails."""
