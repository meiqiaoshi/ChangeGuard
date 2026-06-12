"""Tests for the register-table CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.registry import load_registry
from changeguard.workspace import init_workspace


def test_register_table_command_adds_table_to_registry(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    schema = project / "examples" / "schemas" / "sales_schema.json"
    contract = project / "examples" / "contracts" / "sales_contract.yml"
    schema.parent.mkdir(parents=True)
    contract.parent.mkdir(parents=True)
    schema.write_text('{"table": "sales"}\n', encoding="utf-8")
    contract.write_text("table: sales\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "register-table",
            "--name",
            "sales",
            "--schema",
            "examples/schemas/sales_schema.json",
            "--contract",
            "examples/contracts/sales_contract.yml",
        ],
    )

    assert result.exit_code == 0
    assert "Registered table: sales" in result.stdout

    registry = load_registry(project)
    assert len(registry.tables) == 1
    assert registry.tables[0].name == "sales"
    assert registry.tables[0].schema_path == "examples/schemas/sales_schema.json"
    assert registry.tables[0].contract_path == "examples/contracts/sales_contract.yml"


def test_register_table_command_reports_missing_schema(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "register-table",
            "--name",
            "sales",
            "--schema",
            "missing.json",
        ],
    )

    assert result.exit_code == 1
    assert "Schema file not found" in result.output
