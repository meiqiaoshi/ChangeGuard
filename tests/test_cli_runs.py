"""Tests for the runs CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.audit import save_review_run
from changeguard.cli import app
from changeguard.models import Decision, ReviewResult, RiskLevel
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_runs_command_lists_saved_review_run(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
    )

    runner = CliRunner()
    propose_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "add_discount_column.yml")],
    )
    assert propose_result.exit_code == 0

    runs_result = runner.invoke(app, ["runs"])
    assert runs_result.exit_code == 0
    assert "run_id\tdecision\trisk_level\tchange_type\ttarget\tcreated_at" in runs_result.stdout
    assert "000001" in runs_result.stdout
    assert "ALLOW" in runs_result.stdout
    assert "LOW" in runs_result.stdout
    assert "add_column" in runs_result.stdout
    assert "sales.discount" in runs_result.stdout


def test_runs_command_reports_empty_workspace(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    result = runner.invoke(app, ["runs"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "No review runs saved."


def test_runs_command_lists_legacy_runs_without_change_metadata(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)
    save_review_run(
        project,
        ReviewResult(decision=Decision.WARN, risk_level=RiskLevel.MEDIUM),
    )

    runner = CliRunner()
    result = runner.invoke(app, ["runs"])

    assert result.exit_code == 0
    assert "000001\tWARN\tMEDIUM\t(unknown)\t(unknown)" in result.stdout
