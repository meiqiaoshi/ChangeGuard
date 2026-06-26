"""Tests for the review-run CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_review_run_command_renders_saved_decision(tmp_path: Path, monkeypatch) -> None:
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
    propose_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )
    assert propose_result.exit_code == 0

    review_result = runner.invoke(app, ["review-run", "000001"])

    assert review_result.exit_code == 0
    assert "Decision: BLOCK" in review_result.stdout
    assert "Risk Level:" in review_result.stdout
    assert "Recommended Migration Plan:" in review_result.stdout
    assert "Rollback Notes:" in review_result.stdout
    assert "mart_daily_revenue.total_amount" in review_result.stdout


def test_review_run_command_accepts_unpadded_run_id(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "add_discount_column.yml")],
    )

    result = runner.invoke(app, ["review-run", "1"])

    assert result.exit_code == 0
    assert "Decision: ALLOW" in result.stdout


def test_review_run_command_reports_missing_run(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    result = runner.invoke(app, ["review-run", "000099"])

    assert result.exit_code == 1
    assert "Review run not found: 000099" in result.output
