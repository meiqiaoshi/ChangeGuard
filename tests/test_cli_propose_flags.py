"""Tests for propose command with CLI flags."""

from typer.testing import CliRunner

from changeguard.cli import app


def test_propose_command_parses_rename_column_flags() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "propose",
            "--change-type",
            "rename_column",
            "--table",
            "sales",
            "--column",
            "amount",
            "--new-name",
            "order_amount",
        ],
    )

    assert result.exit_code == 0
    assert "change_type: rename_column" in result.stdout
    assert "table: sales" in result.stdout
    assert "column: amount" in result.stdout
    assert "new_name: order_amount" in result.stdout


def test_propose_command_parses_add_column_flags() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "propose",
            "--change-type",
            "add_column",
            "--table",
            "sales",
            "--column",
            "discount",
            "--type",
            "float",
            "--nullable",
            "true",
        ],
    )

    assert result.exit_code == 0
    assert "change_type: add_column" in result.stdout
    assert "table: sales" in result.stdout
    assert "column: discount" in result.stdout
    assert "type: float" in result.stdout
    assert "nullable: true" in result.stdout


def test_propose_command_requires_file_or_flags() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["propose"])

    assert result.exit_code == 1
    assert "Provide --file or --change-type" in result.output
