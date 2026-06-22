"""Tests for the change review planner skeleton."""

from pathlib import Path

from changeguard.models import ChangeRequest, ChangeType, Decision, RiskLevel
from changeguard.planner import review_change


def test_review_change_returns_review_result_without_registered_table(tmp_path: Path) -> None:
    request = ChangeRequest(
        change_type=ChangeType.ADD_COLUMN,
        table="sales",
        column="discount",
        column_type="float",
        nullable=True,
    )

    result = review_change(tmp_path, request)

    assert result.decision == Decision.ALLOW
    assert result.risk_level == RiskLevel.LOW
    assert result.check_results == []
