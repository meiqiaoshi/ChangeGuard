"""Workspace path helpers and initialization."""

import json
from pathlib import Path

WORKSPACE_DIR_NAME = ".changeguard"
REGISTRY_FILE_NAME = "registry.json"
CONFIG_FILE_NAME = "config.json"
RUNS_DIR_NAME = "runs"


def workspace_root(base: Path | None = None) -> Path:
    """Return the ChangeGuard workspace root directory."""
    return (base or Path.cwd()) / WORKSPACE_DIR_NAME


def registry_path(base: Path | None = None) -> Path:
    """Return the path to the table registry file."""
    return workspace_root(base) / REGISTRY_FILE_NAME


def config_path(base: Path | None = None) -> Path:
    """Return the path to the workspace config file."""
    return workspace_root(base) / CONFIG_FILE_NAME


def runs_path(base: Path | None = None) -> Path:
    """Return the path to the review runs directory."""
    return workspace_root(base) / RUNS_DIR_NAME


DEFAULT_REGISTRY: dict = {"tables": []}
DEFAULT_CONFIG: dict = {"version": "1.0"}


def init_workspace(path: Path) -> None:
    """Create the ChangeGuard workspace directories and default files."""
    workspace_root(path).mkdir(parents=True, exist_ok=True)
    runs_path(path).mkdir(parents=True, exist_ok=True)

    registry_file = registry_path(path)
    if not registry_file.exists():
        registry_file.write_text(
            json.dumps(DEFAULT_REGISTRY, indent=2) + "\n",
            encoding="utf-8",
        )

    config_file = config_path(path)
    if not config_file.exists():
        config_file.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2) + "\n",
            encoding="utf-8",
        )
