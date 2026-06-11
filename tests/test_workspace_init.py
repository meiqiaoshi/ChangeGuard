"""Tests for workspace initialization."""

import json
from pathlib import Path

from changeguard.workspace import (
    config_path,
    init_workspace,
    registry_path,
    runs_path,
    workspace_root,
)


def test_init_workspace_creates_directories_and_files(tmp_path: Path) -> None:
    init_workspace(tmp_path)

    assert workspace_root(tmp_path).is_dir()
    assert runs_path(tmp_path).is_dir()
    assert registry_path(tmp_path).is_file()
    assert config_path(tmp_path).is_file()


def test_init_workspace_writes_default_registry(tmp_path: Path) -> None:
    init_workspace(tmp_path)

    registry = json.loads(registry_path(tmp_path).read_text(encoding="utf-8"))
    assert registry == {"tables": []}


def test_init_workspace_writes_default_config(tmp_path: Path) -> None:
    init_workspace(tmp_path)

    config = json.loads(config_path(tmp_path).read_text(encoding="utf-8"))
    assert config == {"version": "1.0"}


def test_init_workspace_is_idempotent(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    registry_path(tmp_path).write_text('{"tables": [{"name": "sales"}]}\n', encoding="utf-8")

    init_workspace(tmp_path)

    registry = json.loads(registry_path(tmp_path).read_text(encoding="utf-8"))
    assert registry == {"tables": [{"name": "sales"}]}
