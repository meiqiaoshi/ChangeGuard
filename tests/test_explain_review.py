"""Tests for deterministic review explanations."""

from changeguard.explain import explain_review
from changeguard.models import (
    CheckResult,
    CheckStatus,
    Decision,
    MigrationPlan,
    MigrationStep,
    ReviewResult,
    RiskLevel,
)


def test_explain_review_includes_decision_and_risk_for_block() -> None:
    result = ReviewResult(
        decision=Decision.BLOCK,
        risk_level=RiskLevel.HIGH,
        reasons=["Column amount is required by contract for table sales"],
        check_results=[
            CheckResult(
                name="contract_rename_required_column",
                status=CheckStatus.FAIL,
                message="Column amount is required by contract for table sales",
            )
        ],
        impacted_assets=["mart_daily_revenue.total_amount"],
        migration_plan=MigrationPlan(
            steps=[
                MigrationStep(
                    step_number=1,
                    title="Add new column as nullable",
                    description="Add order_amount as nullable.",
                    required=True,
                )
            ]
        ),
        rollback_notes=["Do not delete old data files"],
    )

    explanation = explain_review(result)

    assert "BLOCK decision" in explanation
    assert "HIGH risk" in explanation
    assert "failed one or more safety checks" in explanation
    assert "Column amount is required by contract for table sales" in explanation
    assert "mart_daily_revenue.total_amount" in explanation
    assert "Add new column as nullable" in explanation
    assert "Do not delete old data files" in explanation


def test_explain_review_includes_decision_and_risk_for_allow() -> None:
    result = ReviewResult(
        decision=Decision.ALLOW,
        risk_level=RiskLevel.LOW,
        check_results=[
            CheckResult(
                name="contract_add_nullable_column",
                status=CheckStatus.PASS,
                message="Adding nullable column promo_code is allowed by contract",
            )
        ],
    )

    explanation = explain_review(result)

    assert "ALLOW decision" in explanation
    assert "LOW risk" in explanation
    assert "passed all safety checks" in explanation


def test_explain_review_summarizes_warn_decision() -> None:
    result = ReviewResult(
        decision=Decision.WARN,
        risk_level=RiskLevel.MEDIUM,
        reasons=["Column status is defined in contract for table sales and should be reviewed before dropping"],
    )

    explanation = explain_review(result)

    assert "WARN decision" in explanation
    assert "MEDIUM risk" in explanation
    assert "warnings that should be reviewed" in explanation
