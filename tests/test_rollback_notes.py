"""Tests for rollback notes in change reviews."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.changes import load_change_request, validate_rename_column
from changeguard.cli import app
from changeguard.models import ChangeRequest, ChangeType, Decision
from changeguard.planner import generate_rollback_notes, review_change
from changeguard.registry import register_table
from changeguard.render import render_review_result
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_generate_rollback_notes_for_risky_changes() -> None:
    assert generate_rollback_notes(Decision.BLOCK) == [
        "Keep old column until downstream validation passes",
        "Do not delete old data files",
        "Restore previous contract version if checks fail",
    ]
    assert generate_rollback_notes(Decision.WARN) == [
        "Keep old column until downstream validation passes",
        "Do not delete old data files",
        "Restore previous contract version if checks fail",
    ]
    assert generate_rollback_notes(Decision.ALLOW) == []


def test_review_change_includes_rollback_notes_for_blocked_rename(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
        lineage_path=str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
    )

    request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )
    result = review_change(project, request)

    assert result.decision == Decision.BLOCK
    assert len(result.rollback_notes) == 3
    assert "Do not delete old data files" in result.rollback_notes


def test_render_review_result_includes_rollback_notes_for_risky_change(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
        lineage_path=str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
    )

    result = review_change(
        project,
        ChangeRequest(
            change_type=ChangeType.DROP_COLUMN,
            table="sales",
            column="status",
        ),
    )

    output = render_review_result(result)

    assert result.decision.value == "WARN"
    assert "Rollback Notes" in output
    assert "- Keep old column until downstream validation passes" in output
    assert "- Restore previous contract version if checks fail" in output


def test_propose_blocked_rename_includes_rollback_notes(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
        lineage_path=str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
    )

    runner = CliRunner()
    cli_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )

    assert cli_result.exit_code == 0
    assert "Rollback Notes" in cli_result.stdout
    assert "Do not delete old data files" in cli_result.stdout
