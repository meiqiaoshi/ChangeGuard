"""Tests for the explain-run CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_explain_run_command_outputs_narrative_for_saved_review(
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
    propose_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "block_rename_required_column.yml")],
    )
    assert propose_result.exit_code == 0

    explain_result = runner.invoke(app, ["explain-run", "000001"])

    assert explain_result.exit_code == 0
    assert "BLOCK decision" in explain_result.stdout
    assert "CRITICAL risk" in explain_result.stdout or "HIGH risk" in explain_result.stdout
    assert "failed one or more safety checks" in explain_result.stdout
    assert "mart_daily_revenue.total_amount" in explain_result.stdout
    assert "Add new column as nullable" in explain_result.stdout
    assert "Do not delete old data files" in explain_result.stdout


def test_explain_run_command_accepts_unpadded_run_id(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "allow_add_nullable_column.yml")],
    )

    result = runner.invoke(app, ["explain-run", "1"])

    assert result.exit_code == 0
    assert "ALLOW decision" in result.stdout
    assert "LOW risk" in result.stdout


def test_explain_run_command_reports_missing_run(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    result = runner.invoke(app, ["explain-run", "000099"])

    assert result.exit_code == 1
    assert "Review run not found: 000099" in result.output
