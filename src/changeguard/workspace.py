"""Workspace path helpers and initialization."""

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
