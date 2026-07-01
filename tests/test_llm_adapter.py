"""Tests for optional LLM adapter skeleton."""

from changeguard.explain import explain_review
from changeguard.llm import LLMClient, NoOpLLMClient, OpenAICompatibleClient
from changeguard.models import Decision, ReviewResult, RiskLevel


def test_noop_llm_client_uses_deterministic_explanation() -> None:
    review = ReviewResult(
        decision=Decision.BLOCK,
        risk_level=RiskLevel.HIGH,
        reasons=["Column amount is required by contract for table sales"],
    )
    client = NoOpLLMClient()

    explanation = client.explain_review(review)

    assert explanation == explain_review(review)
    assert "BLOCK decision" in explanation
    assert "HIGH risk" in explanation


def test_openai_compatible_client_placeholder_falls_back_without_api_key() -> None:
    review = ReviewResult(decision=Decision.ALLOW, risk_level=RiskLevel.LOW)
    client = OpenAICompatibleClient(model="gpt-4o-mini", api_key=None)

    explanation = client.explain_review(review)

    assert explanation == explain_review(review)
    assert client.api_key is None
    assert client.model == "gpt-4o-mini"


def test_llm_client_interface_is_implemented_by_adapters() -> None:
    assert isinstance(NoOpLLMClient(), LLMClient)
    assert isinstance(OpenAICompatibleClient(), LLMClient)
