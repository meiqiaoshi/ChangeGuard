"""Tests for the impact CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def _setup_sales_with_lineage(project: Path) -> None:
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
        lineage_path=str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
    )


def test_impact_command_lists_table_downstream_assets(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    _setup_sales_with_lineage(project)

    runner = CliRunner()
    result = runner.invoke(app, ["impact", "sales"])

    assert result.exit_code == 0
    assert "Impacted assets for sales:" in result.stdout
    assert "mart_daily_revenue" in result.stdout
    assert "customer_orders_summary" in result.stdout
    assert "sales_dashboard" in result.stdout


def test_impact_command_lists_column_downstream_assets(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    _setup_sales_with_lineage(project)

    runner = CliRunner()
    result = runner.invoke(app, ["impact", "sales.amount"])

    assert result.exit_code == 0
    assert "Impacted assets for sales.amount:" in result.stdout
    assert "mart_daily_revenue" in result.stdout
    assert "sales_dashboard" in result.stdout
    assert "column: total_amount" in result.stdout


def test_impact_command_reports_missing_table(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()
    result = runner.invoke(app, ["impact", "missing.amount"])

    assert result.exit_code == 1
    assert "Table not found: missing" in result.output
