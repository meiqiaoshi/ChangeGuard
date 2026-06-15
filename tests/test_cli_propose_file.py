"""Tests for propose command with YAML change requests."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "change_requests"


def test_propose_command_prints_parsed_yaml_change_request() -> None:
    runner = CliRunner()
    change_file = EXAMPLES_DIR / "rename_amount_column.yml"

    result = runner.invoke(app, ["propose", "--file", str(change_file)])

    assert result.exit_code == 0
    assert "change_type: rename_column" in result.stdout
    assert "table: sales" in result.stdout
    assert "column: amount" in result.stdout
    assert "new_name: order_amount" in result.stdout
    assert "Rename amount to order_amount" in result.stdout


def test_propose_command_reports_missing_file(tmp_path: Path) -> None:
    runner = CliRunner()
    missing = tmp_path / "missing.yml"

    result = runner.invoke(app, ["propose", "--file", str(missing)])

    assert result.exit_code == 1
    assert "Change request file not found" in result.output
