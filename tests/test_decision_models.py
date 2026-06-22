"""Tests for review decision models."""

from changeguard.models import (
    CheckResult,
    CheckStatus,
    Decision,
    ReviewResult,
    RiskLevel,
)


def test_review_result_model() -> None:
    result = ReviewResult(
        decision=Decision.BLOCK,
        risk_level=RiskLevel.HIGH,
        reasons=["sales.amount is required by contract"],
        check_results=[
            CheckResult(
                name="contract_rename_required_column",
                status=CheckStatus.FAIL,
                message="sales.amount is required by contract",
            )
        ],
        impacted_assets=["mart_daily_revenue.total_amount"],
    )

    assert result.decision == Decision.BLOCK
    assert result.risk_level == RiskLevel.HIGH
    assert len(result.check_results) == 1
    assert result.impacted_assets[0] == "mart_daily_revenue.total_amount"


def test_review_result_serialization_round_trip() -> None:
    result = ReviewResult(
        decision=Decision.ALLOW,
        risk_level=RiskLevel.LOW,
        reasons=["Adding nullable column is allowed"],
        check_results=[
            CheckResult(
                name="contract_add_nullable_column",
                status=CheckStatus.PASS,
                message="Adding nullable column discount is allowed by contract",
            )
        ],
    )

    payload = result.model_dump(mode="json")
    restored = ReviewResult.model_validate(payload)

    assert restored == result


def test_decision_and_risk_level_values() -> None:
    assert Decision.WARN.value == "WARN"
    assert RiskLevel.CRITICAL.value == "CRITICAL"
