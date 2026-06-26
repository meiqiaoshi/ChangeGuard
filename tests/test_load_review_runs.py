"""Tests for loading saved review audit logs."""

from pathlib import Path

import pytest

from changeguard.audit import ReviewRunNotFoundError, list_runs, load_run, save_review_run
from changeguard.models import (
    CheckResult,
    CheckStatus,
    Decision,
    MigrationPlan,
    MigrationStep,
    ReviewResult,
    RiskLevel,
)
from changeguard.workspace import init_workspace


def test_save_and_load_review_run_round_trip(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    review_result = ReviewResult(
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

    save_review_run(tmp_path, review_result)
    loaded = load_run(tmp_path, "000001")

    assert loaded == review_result


def test_list_runs_returns_saved_run_ids_in_order(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    save_review_run(tmp_path, ReviewResult(decision=Decision.ALLOW, risk_level=RiskLevel.LOW))
    save_review_run(tmp_path, ReviewResult(decision=Decision.WARN, risk_level=RiskLevel.MEDIUM))
    save_review_run(tmp_path, ReviewResult(decision=Decision.BLOCK, risk_level=RiskLevel.HIGH))

    assert list_runs(tmp_path) == ["000001", "000002", "000003"]


def test_load_run_normalizes_numeric_run_id(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    save_review_run(tmp_path, ReviewResult(decision=Decision.ALLOW, risk_level=RiskLevel.LOW))

    loaded = load_run(tmp_path, "1")

    assert loaded.decision == Decision.ALLOW


def test_load_run_raises_for_missing_run(tmp_path: Path) -> None:
    init_workspace(tmp_path)

    with pytest.raises(ReviewRunNotFoundError, match="Review run not found: 000099"):
        load_run(tmp_path, "000099")
