"""Verify ChangeGuard package and module imports."""

import importlib

import pytest

import changeguard
from changeguard import (
    audit,
    changes,
    cli,
    contracts,
    lineage,
    models,
    planner,
    registry,
    render,
    rules,
    schema,
    workspace,
)

MODULES = [
    audit,
    changes,
    cli,
    contracts,
    lineage,
    models,
    planner,
    registry,
    render,
    rules,
    schema,
    workspace,
]


def test_package_version() -> None:
    assert changeguard.__version__ == "0.1.0"


def test_top_level_modules_importable() -> None:
    for module in MODULES:
        assert module.__name__.startswith("changeguard.")


@pytest.mark.parametrize(
    "module_name",
    [
        "changeguard",
        "changeguard.audit",
        "changeguard.changes",
        "changeguard.cli",
        "changeguard.contracts",
        "changeguard.lineage",
        "changeguard.models",
        "changeguard.planner",
        "changeguard.registry",
        "changeguard.render",
        "changeguard.rules",
        "changeguard.schema",
        "changeguard.workspace",
    ],
)
def test_module_import_by_name(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module is not None
