"""Tests for tables and inspect CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.registry import register_table
from changeguard.workspace import init_workspace


def _setup_registered_table(project: Path) -> None:
    init_workspace(project)
    schema = project / "schema.json"
    contract = project / "contract.yml"
    schema.write_text('{"table": "sales"}\n', encoding="utf-8")
    contract.write_text("table: sales\n", encoding="utf-8")
    register_table(
        project,
        name="sales",
        schema_path="schema.json",
        contract_path="contract.yml",
        owner="analytics-team",
        description="Core sales fact table",
        tags=["fact", "core"],
    )


def test_tables_command_lists_registered_table(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    _setup_registered_table(project)

    runner = CliRunner()
    result = runner.invoke(app, ["tables"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "sales"


def test_inspect_command_shows_registered_table_metadata(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    _setup_registered_table(project)

    runner = CliRunner()
    result = runner.invoke(app, ["inspect", "sales"])

    assert result.exit_code == 0
    assert "name: sales" in result.stdout
    assert "schema path: schema.json" in result.stdout
    assert "contract path: contract.yml" in result.stdout
    assert "owner: analytics-team" in result.stdout
    assert "tags: fact, core" in result.stdout
    assert "description: Core sales fact table" in result.stdout


def test_inspect_command_reports_missing_table(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    result = runner.invoke(app, ["inspect", "missing"])

    assert result.exit_code == 1
    assert "Table not found: missing" in result.output
