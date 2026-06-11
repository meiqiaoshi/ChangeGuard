"""Tests for the init CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.cli import app
from changeguard.workspace import config_path, registry_path, runs_path, workspace_root


def test_init_command_creates_workspace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "Initialized ChangeGuard workspace at .changeguard"
    assert workspace_root(tmp_path).is_dir()
    assert runs_path(tmp_path).is_dir()
    assert registry_path(tmp_path).is_file()
    assert config_path(tmp_path).is_file()


def test_init_command_with_path_option(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    runner = CliRunner()

    result = runner.invoke(app, ["init", "--path", str(project_dir)])

    assert result.exit_code == 0
    assert workspace_root(project_dir).is_dir()
