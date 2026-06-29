"""End-to-end tests for lineage impact analysis workflows."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.changes import load_change_request, validate_rename_column
from changeguard.cli import app
from changeguard.lineage import find_column_impact, load_lineage
from changeguard.models import CheckStatus
from changeguard.registry import get_table
from changeguard.rules import check_change_against_lineage
from changeguard.workspace import init_workspace, registry_path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _load_sales_lineage(project: Path):
    table = get_table(project, "sales")
    lineage_file = Path(table.lineage_path)
    if not lineage_file.is_absolute():
        lineage_file = project / lineage_file
    return load_lineage(lineage_file)


def test_phase4_end_to_end_lineage_impact_analysis(tmp_path: Path, monkeypatch) -> None:
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

    impact_result = runner.invoke(app, ["impact", "sales.amount"])
    assert impact_result.exit_code == 0
    assert "Impacted assets for sales.amount:" in impact_result.stdout
    assert "mart_daily_revenue" in impact_result.stdout
    assert "sales_dashboard" in impact_result.stdout

    graph = _load_sales_lineage(project)
    impacts = find_column_impact(graph, "sales.amount")
    assert {impact.asset.name for impact in impacts} >= {
        "mart_daily_revenue",
        "sales_dashboard",
    }

    rename_request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )
    lineage_results = check_change_against_lineage(graph, rename_request)
    assert lineage_results[0].status == CheckStatus.FAIL
    assert "mart_daily_revenue" in lineage_results[0].message

    propose_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )
    assert propose_result.exit_code == 0
    assert "Decision\nBLOCK" in propose_result.stdout
    assert "Impacted Assets" in propose_result.stdout
    assert "mart_daily_revenue.total_amount" in propose_result.stdout
    assert "Checks" in propose_result.stdout
    assert "(lineage)" in propose_result.stdout
    assert "[FAIL]" in propose_result.stdout
