"""Tests for workspace path helpers."""

from pathlib import Path

from changeguard.workspace import (
    CONFIG_FILE_NAME,
    REGISTRY_FILE_NAME,
    RUNS_DIR_NAME,
    WORKSPACE_DIR_NAME,
    config_path,
    registry_path,
    runs_path,
    workspace_root,
)


def test_workspace_root_default_base(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert workspace_root() == tmp_path / WORKSPACE_DIR_NAME


def test_workspace_root_with_explicit_base(tmp_path: Path) -> None:
    base = tmp_path / "project"
    assert workspace_root(base) == base / WORKSPACE_DIR_NAME


def test_registry_path(tmp_path: Path) -> None:
    base = tmp_path / "project"
    assert registry_path(base) == base / WORKSPACE_DIR_NAME / REGISTRY_FILE_NAME


def test_config_path(tmp_path: Path) -> None:
    base = tmp_path / "project"
    assert config_path(base) == base / WORKSPACE_DIR_NAME / CONFIG_FILE_NAME


def test_runs_path(tmp_path: Path) -> None:
    base = tmp_path / "project"
    assert runs_path(base) == base / WORKSPACE_DIR_NAME / RUNS_DIR_NAME
