"""Tests for the check-contract CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_check_contract_command_prints_contract_summary(tmp_path: Path, monkeypatch) -> None:
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
    result = runner.invoke(app, ["check-contract", "sales"])

    assert result.exit_code == 0
    assert "table: sales" in result.stdout
    assert "version: 1.0" in result.stdout
    assert "owner: analytics-team" in result.stdout
    assert "columns: 5" in result.stdout
    assert "required columns:" in result.stdout
    assert "amount" in result.stdout
    assert "rules: 2" in result.stdout


def test_check_contract_command_reports_missing_table(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    result = runner.invoke(app, ["check-contract", "missing"])

    assert result.exit_code == 1
    assert "Table not found: missing" in result.output
