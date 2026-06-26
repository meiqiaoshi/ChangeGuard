"""Tests for saving audit logs from the propose command."""

import json
from pathlib import Path

from typer.testing import CliRunner

from changeguard.audit import load_run
from changeguard.cli import app
from changeguard.models import Decision
from changeguard.registry import register_table
from changeguard.workspace import init_workspace, runs_path

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_propose_command_saves_audit_log_and_prints_path(tmp_path: Path, monkeypatch) -> None:
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
    assert "Audit log: .changeguard/runs/000001.json" in result.stdout

    audit_file = runs_path(project) / "000001.json"
    assert audit_file.is_file()

    payload = json.loads(audit_file.read_text(encoding="utf-8"))
    assert payload["run_id"] == "000001"
    assert payload["decision"] == "ALLOW"

    loaded = load_run(project, "000001")
    assert loaded.decision == Decision.ALLOW


def test_propose_command_assigns_incremental_audit_logs(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)

    runner = CliRunner()

    first = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "add_discount_column.yml")],
    )
    second = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert "Audit log: .changeguard/runs/000001.json" in first.stdout
    assert "Audit log: .changeguard/runs/000002.json" in second.stdout
    assert (runs_path(project) / "000001.json").is_file()
    assert (runs_path(project) / "000002.json").is_file()
