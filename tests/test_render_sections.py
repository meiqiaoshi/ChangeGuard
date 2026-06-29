"""Tests for sectioned CLI review output."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.changes import load_change_request, validate_rename_column
from changeguard.cli import app
from changeguard.models import (
    CheckResult,
    CheckStatus,
    Decision,
    MigrationPlan,
    MigrationStep,
    ReviewResult,
    RiskLevel,
)
from changeguard.render import render_propose_output, render_review_result

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_render_review_result_includes_section_headings() -> None:
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

    output = render_review_result(result)

    for heading in (
        "Decision",
        "Risk Level",
        "Checks",
        "Impacted Assets",
        "Reasons",
        "Migration Plan",
        "Rollback Notes",
    ):
        assert heading in output


def test_render_propose_output_includes_all_sections(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    runner = CliRunner()
    from changeguard.registry import register_table
    from changeguard.workspace import init_workspace

    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
        lineage_path=str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
    )

    result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )

    assert result.exit_code == 0
    for heading in (
        "Change Request",
        "Decision",
        "Risk Level",
        "Checks",
        "Impacted Assets",
        "Migration Plan",
        "Rollback Notes",
        "Audit Log",
    ):
        assert heading in result.stdout
    assert ".changeguard/runs/000001.json" in result.stdout


def test_render_propose_output_orders_sections() -> None:
    request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )
    review = ReviewResult(
        decision=Decision.BLOCK,
        risk_level=RiskLevel.HIGH,
        rollback_notes=["Do not delete old data files"],
    )

    output = render_propose_output(
        request,
        review,
        audit_log_path=".changeguard/runs/000001.json",
    )

    change_request_index = output.index("Change Request")
    decision_index = output.index("Decision")
    audit_log_index = output.index("Audit Log")
    assert change_request_index < decision_index < audit_log_index
