"""Tests for rendering migration plans in review output."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.changes import load_change_request, validate_rename_column
from changeguard.cli import app
from changeguard.models import MigrationPlan, MigrationStep, ReviewResult, Decision, RiskLevel
from changeguard.planner import generate_rename_column_migration_plan, review_change
from changeguard.registry import register_table
from changeguard.render import render_migration_plan, render_review_result
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_render_migration_plan_lists_numbered_steps() -> None:
    plan = MigrationPlan(
        steps=[
            MigrationStep(
                step_number=1,
                title="Add new column as nullable",
                description="Add order_amount as nullable.",
                required=True,
            ),
            MigrationStep(
                step_number=2,
                title="Backfill new column from old column",
                description="Copy amount into order_amount.",
                required=True,
            ),
        ]
    )

    output = render_migration_plan(plan)

    assert output == (
        "Migration Plan\n"
        "1. Add new column as nullable\n"
        "2. Backfill new column from old column"
    )


def test_render_review_result_includes_migration_plan() -> None:
    request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )
    plan = generate_rename_column_migration_plan(
        request,
        impacted_assets=["mart_daily_revenue.total_amount"],
    )
    assert plan is not None

    result = ReviewResult(
        decision=Decision.BLOCK,
        risk_level=RiskLevel.HIGH,
        migration_plan=plan,
    )

    output = render_review_result(result)

    assert "Migration Plan" in output
    assert "1. Add new column as nullable" in output
    assert "6. Deprecate old column after compatibility window" in output


def test_propose_blocked_rename_includes_migration_plan_in_cli_output(
    tmp_path: Path, monkeypatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
        lineage_path=str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )

    assert result.exit_code == 0
    assert "Decision\nBLOCK" in result.stdout
    assert "Migration Plan" in result.stdout
    assert "1. Add new column as nullable" in result.stdout
    assert "3. Update downstream assets" in result.stdout

    review = review_change(
        project,
        validate_rename_column(
            load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
        ),
    )
    assert review.migration_plan is not None
