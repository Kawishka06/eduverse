class AIOrchestratorError(Exception):
    """Raised when an AI workflow fails or returns an unexpected payload."""


class FalAPIError(AIOrchestratorError):
    """Raised when a fal.ai request fails."""


class LLMError(AIOrchestratorError):
    """Raised when the tutor LLM request fails."""
