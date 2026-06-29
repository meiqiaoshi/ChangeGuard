"""End-to-end tests for the decision engine and full propose review flow."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.workspace import init_workspace, registry_path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _register_sales_with_metadata(runner: CliRunner) -> None:
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


def test_phase5_end_to_end_decision_engine(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    runner = CliRunner()

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0
    assert registry_path(project).is_file()

    _register_sales_with_metadata(runner)

    add_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "add_discount_column.yml")],
    )
    assert add_result.exit_code == 0
    assert "Decision\nALLOW" in add_result.stdout
    assert "Risk Level\nLOW" in add_result.stdout
    assert "(contract)" in add_result.stdout

    rename_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )
    assert rename_result.exit_code == 0
    assert "Decision\nBLOCK" in rename_result.stdout
    assert "Risk Level\n" in rename_result.stdout
    assert any(level in rename_result.stdout for level in ("Risk Level\nHIGH", "Risk Level\nCRITICAL"))
    assert "(contract)" in rename_result.stdout
    assert "(lineage)" in rename_result.stdout
    assert "mart_daily_revenue.total_amount" in rename_result.stdout

    drop_result = runner.invoke(
        app,
        [
            "propose",
            "--change-type",
            "drop_column",
            "--table",
            "sales",
            "--column",
            "status",
        ],
    )
    assert drop_result.exit_code == 0
    assert "Decision\nWARN" in drop_result.stdout
    assert "Risk Level\nMEDIUM" in drop_result.stdout
    assert "contract_drop_optional_column" not in drop_result.stdout
    assert "optional" in drop_result.stdout.lower() or "reviewed before dropping" in drop_result.stdout
    assert "no known downstream dependencies" in drop_result.stdout
