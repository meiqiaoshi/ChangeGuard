"""Tests for propose command running the full review planner."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def _setup_sales_with_contract_and_lineage(project: Path) -> None:
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
        lineage_path=str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
    )


def test_propose_rename_runs_full_review_and_blocks(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    _setup_sales_with_contract_and_lineage(project)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )

    assert result.exit_code == 0
    assert "change_type: rename_column" in result.stdout
    assert "Decision\nBLOCK" in result.stdout
    assert "Risk Level\n" in result.stdout
    assert any(level in result.stdout for level in ("Risk Level\nHIGH", "Risk Level\nCRITICAL"))
    assert "Checks" in result.stdout
    assert "(contract)" in result.stdout
    assert "(lineage)" in result.stdout
    assert "Impacted Assets" in result.stdout
    assert "mart_daily_revenue.total_amount" in result.stdout
    assert "Reasons" in result.stdout


def test_propose_add_nullable_column_runs_full_review_and_allows(
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
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "add_discount_column.yml")],
    )

    assert result.exit_code == 0
    assert "change_type: add_column" in result.stdout
    assert "Decision\nALLOW" in result.stdout
    assert "Risk Level\nLOW" in result.stdout
    assert "(contract)" in result.stdout
