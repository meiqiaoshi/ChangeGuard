"""End-to-end tests for migration planning in change reviews."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.changes import load_change_request, validate_rename_column
from changeguard.cli import app
from changeguard.planner import review_change
from changeguard.workspace import init_workspace, registry_path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def test_phase6_end_to_end_blocked_rename_includes_migration_and_rollback(
    tmp_path: Path, monkeypatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    runner = CliRunner()

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0
    assert registry_path(project).is_file()

    register_result = runner.invoke(
        app,
        [
            "register-table",
            "--name",
            "sales",
            "--schema",
            str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
            "--contract",
            str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
            "--lineage",
            str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
        ],
    )
    assert register_result.exit_code == 0

    request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )
    review = review_change(project, request)

    assert review.decision.value == "BLOCK"
    assert review.risk_level.value in {"HIGH", "CRITICAL"}
    assert review.migration_plan is not None
    assert len(review.migration_plan.steps) >= 6
    assert len(review.rollback_notes) == 3
    assert "mart_daily_revenue.total_amount" in review.impacted_assets

    propose_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )
    assert propose_result.exit_code == 0
    assert "Decision\nBLOCK" in propose_result.stdout
    assert "Risk Level\n" in propose_result.stdout
    assert any(level in propose_result.stdout for level in ("Risk Level\nHIGH", "Risk Level\nCRITICAL"))
    assert "Migration Plan" in propose_result.stdout
    assert "1. Add new column as nullable" in propose_result.stdout
    assert "Rollback Notes" in propose_result.stdout
    assert "Do not delete old data files" in propose_result.stdout
    assert "Impacted Assets" in propose_result.stdout
    assert "mart_daily_revenue.total_amount" in propose_result.stdout
    assert "sales_dashboard.revenue_kpi" in propose_result.stdout
