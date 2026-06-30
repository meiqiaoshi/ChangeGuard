"""Smoke test for the ChangeGuard demo workflow without shell script dependency."""

import json
from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.workspace import registry_path, runs_path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def test_phase8_demo_workflow_smoke(tmp_path: Path, monkeypatch) -> None:
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

    tables_result = runner.invoke(app, ["tables"])
    assert tables_result.exit_code == 0
    assert "sales" in tables_result.stdout

    inspect_result = runner.invoke(app, ["inspect", "sales"])
    assert inspect_result.exit_code == 0
    assert "name: sales" in inspect_result.stdout
    assert "sales_contract.yml" in inspect_result.stdout

    impact_result = runner.invoke(app, ["impact", "sales.amount"])
    assert impact_result.exit_code == 0
    assert "mart_daily_revenue" in impact_result.stdout
    assert "sales_dashboard" in impact_result.stdout

    allow_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "allow_add_nullable_column.yml")],
    )
    assert allow_result.exit_code == 0
    assert "Change Request" in allow_result.stdout
    assert "Decision\nALLOW" in allow_result.stdout
    assert "Audit Log" in allow_result.stdout
    assert ".changeguard/runs/000001.json" in allow_result.stdout

    block_result = runner.invoke(
        app,
        [
            "propose",
            "--file",
            str(EXAMPLES_DIR / "change_requests" / "block_rename_required_column.yml"),
        ],
    )
    assert block_result.exit_code == 0
    assert "Decision\nBLOCK" in block_result.stdout
    assert "Migration Plan" in block_result.stdout
    assert "Rollback Notes" in block_result.stdout
    assert ".changeguard/runs/000002.json" in block_result.stdout

    assert (runs_path(project) / "000001.json").is_file()
    assert (runs_path(project) / "000002.json").is_file()

    allow_payload = json.loads((runs_path(project) / "000001.json").read_text(encoding="utf-8"))
    block_payload = json.loads((runs_path(project) / "000002.json").read_text(encoding="utf-8"))
    assert allow_payload["decision"] == "ALLOW"
    assert block_payload["decision"] == "BLOCK"

    runs_result = runner.invoke(app, ["runs"])
    assert runs_result.exit_code == 0
    assert "000001" in runs_result.stdout
    assert "000002" in runs_result.stdout
    assert "add_column" in runs_result.stdout
    assert "rename_column" in runs_result.stdout

    review_result = runner.invoke(app, ["review-run", "000001"])
    assert review_result.exit_code == 0
    assert "Decision\nALLOW" in review_result.stdout
    assert "Risk Level\nLOW" in review_result.stdout
