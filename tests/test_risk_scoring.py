"""Tests for risk level scoring."""

from changeguard.models import (
    ChangeRequest,
    ChangeType,
    CheckResult,
    CheckStatus,
    Decision,
    RiskLevel,
)
from changeguard.rules import score_risk_level


def _check(status: CheckStatus, message: str, source: str = "contract") -> CheckResult:
    return CheckResult(
        name="example_check",
        status=status,
        message=message,
        source=source,
    )


def test_score_risk_level_low_for_allow_nullable_add_column() -> None:
    request = ChangeRequest(
        change_type=ChangeType.ADD_COLUMN,
        table="sales",
        column="discount",
        column_type="float",
        nullable=True,
    )

    risk = score_risk_level(
        Decision.ALLOW,
        [_check(CheckStatus.PASS, "nullable add allowed")],
        request,
    )

    assert risk == RiskLevel.LOW


def test_score_risk_level_medium_for_warn() -> None:
    risk = score_risk_level(
        Decision.WARN,
        [_check(CheckStatus.WARN, "optional column rename")],
    )

    assert risk == RiskLevel.MEDIUM


def test_score_risk_level_high_for_block_with_contract_violation() -> None:
    risk = score_risk_level(
        Decision.BLOCK,
        [_check(CheckStatus.FAIL, "required column cannot be renamed")],
    )

    assert risk == RiskLevel.HIGH


def test_score_risk_level_critical_for_block_with_dashboard_impact() -> None:
    risk = score_risk_level(
        Decision.BLOCK,
        [
            _check(
                CheckStatus.FAIL,
                "Column amount is referenced by downstream assets: sales_dashboard.revenue_kpi",
                source="lineage",
            )
        ],
    )

    assert risk == RiskLevel.CRITICAL
