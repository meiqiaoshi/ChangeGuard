"""End-to-end tests for audit log persistence and run review."""

import json
from pathlib import Path

from typer.testing import CliRunner

from changeguard.audit import load_run
from changeguard.cli import app
from changeguard.models import Decision
from changeguard.workspace import init_workspace, registry_path, runs_path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def test_phase7_end_to_end_audit_log_workflow(tmp_path: Path, monkeypatch) -> None:
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

    propose_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )
    assert propose_result.exit_code == 0
    assert "Decision\nBLOCK" in propose_result.stdout
    assert "Audit Log" in propose_result.stdout
    assert ".changeguard/runs/000001.json" in propose_result.stdout

    audit_file = runs_path(project) / "000001.json"
    assert audit_file.is_file()

    payload = json.loads(audit_file.read_text(encoding="utf-8"))
    assert payload["run_id"] == "000001"
    assert payload["decision"] == "BLOCK"
    assert payload["change_type"] == "rename_column"
    assert payload["target"] == "sales.amount"
    assert "created_at" in payload
    assert payload["migration_plan"]["steps"]
    assert payload["rollback_notes"]

    loaded = load_run(project, "000001")
    assert loaded.decision == Decision.BLOCK

    runs_result = runner.invoke(app, ["runs"])
    assert runs_result.exit_code == 0
    assert "run_id\tdecision\trisk_level\tchange_type\ttarget\tcreated_at" in runs_result.stdout
    assert "000001" in runs_result.stdout
    assert "BLOCK" in runs_result.stdout
    assert "rename_column" in runs_result.stdout
    assert "sales.amount" in runs_result.stdout

    review_result = runner.invoke(app, ["review-run", "000001"])
    assert review_result.exit_code == 0
    assert "Decision\nBLOCK" in review_result.stdout
    assert "Migration Plan" in review_result.stdout
    assert "Rollback Notes" in review_result.stdout
    assert "mart_daily_revenue.total_amount" in review_result.stdout
