"""Tests for propose output with lineage impact."""

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


def test_propose_rename_includes_impacted_assets_and_lineage_block(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    _setup_sales_with_lineage(project)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )

    assert result.exit_code == 0
    assert "change_type: rename_column" in result.stdout
    assert "Decision\nBLOCK" in result.stdout
    assert "Impacted Assets" in result.stdout
    assert "mart_daily_revenue.total_amount" in result.stdout
    assert "sales_dashboard.revenue_kpi" in result.stdout
    assert "Checks" in result.stdout
    assert "(lineage)" in result.stdout
    assert "[FAIL]" in result.stdout


def test_propose_drop_includes_impacted_assets_and_lineage_block(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    _setup_sales_with_lineage(project)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "propose",
            "--change-type",
            "drop_column",
            "--table",
            "sales",
            "--column",
            "customer_id",
        ],
    )

    assert result.exit_code == 0
    assert "Impacted Assets" in result.stdout
    assert "customer_orders_summary" in result.stdout
    assert "(lineage)" in result.stdout
    assert "[FAIL]" in result.stdout


def test_propose_rename_without_lineage_still_prints_change_request(tmp_path: Path, monkeypatch) -> None:
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
    result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )

    assert result.exit_code == 0
    assert "change_type: rename_column" in result.stdout
    assert "Decision\nBLOCK" in result.stdout
    assert "(lineage)" not in result.stdout
