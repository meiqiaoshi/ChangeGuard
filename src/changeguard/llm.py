"""Optional LLM adapters for explaining deterministic review results."""

from abc import ABC, abstractmethod

from changeguard.explain import explain_review as deterministic_explain_review
from changeguard.models import ReviewResult


class LLMClient(ABC):
    """Interface for optional AI explanation providers."""

    @abstractmethod
    def explain_review(self, review_result: ReviewResult) -> str:
        """Return a narrative explanation for a completed review result."""


class NoOpLLMClient(LLMClient):
    """Deterministic client that never calls an external model."""

    def explain_review(self, review_result: ReviewResult) -> str:
        return deterministic_explain_review(review_result)


class OpenAICompatibleClient(LLMClient):
    """Placeholder adapter for OpenAI-compatible chat APIs.

    The MVP does not perform live API calls. This class stores connection
    settings for future integration and falls back to the deterministic
    explanation helper.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def explain_review(self, review_result: ReviewResult) -> str:
        return deterministic_explain_review(review_result)
