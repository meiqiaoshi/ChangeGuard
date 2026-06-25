"""Tests for persisting review results as audit logs."""

import json
from pathlib import Path

from changeguard.audit import save_review_run
from changeguard.models import (
    CheckResult,
    CheckStatus,
    Decision,
    MigrationPlan,
    MigrationStep,
    ReviewResult,
    RiskLevel,
)
from changeguard.workspace import init_workspace, runs_path


def test_save_review_run_creates_json_file_with_decision(tmp_path: Path) -> None:
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

    run_file = save_review_run(tmp_path, review_result)

    assert run_file == runs_path(tmp_path) / "000001.json"
    assert run_file.is_file()

    payload = json.loads(run_file.read_text(encoding="utf-8"))
    assert payload["run_id"] == "000001"
    assert payload["decision"] == "BLOCK"
    assert payload["risk_level"] == "HIGH"
    assert payload["reasons"] == ["Column amount is required by contract for table sales"]
    assert payload["check_results"][0]["status"] == "FAIL"
    assert payload["migration_plan"]["steps"][0]["title"] == "Add new column as nullable"
    assert payload["rollback_notes"] == ["Do not delete old data files"]


def test_save_review_run_assigns_sequential_run_files(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    allow_result = ReviewResult(decision=Decision.ALLOW, risk_level=RiskLevel.LOW)
    block_result = ReviewResult(decision=Decision.BLOCK, risk_level=RiskLevel.HIGH)

    first_file = save_review_run(tmp_path, allow_result)
    second_file = save_review_run(tmp_path, block_result)

    assert first_file.name == "000001.json"
    assert second_file.name == "000002.json"
    assert json.loads(first_file.read_text(encoding="utf-8"))["decision"] == "ALLOW"
    assert json.loads(second_file.read_text(encoding="utf-8"))["decision"] == "BLOCK"
