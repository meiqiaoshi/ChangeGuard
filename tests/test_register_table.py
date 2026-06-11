"""Tests for table registration."""

from pathlib import Path

import pytest

from changeguard.registry import DuplicateTableError, load_registry, register_table
from changeguard.workspace import init_workspace


def _write_schema(project: Path, name: str = "schema.json") -> Path:
    schema = project / name
    schema.write_text('{"table": "sales"}\n', encoding="utf-8")
    return schema


def test_register_table_adds_entry_to_registry(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)
    _write_schema(project)

    table, warnings = register_table(
        project,
        name="sales",
        schema_path="schema.json",
        contract_path="missing_contract.yml",
    )

    assert table.name == "sales"
    assert table.schema_path == "schema.json"
    assert table.contract_path == "missing_contract.yml"
    assert "Contract file not found" in warnings[0]

    registry = load_registry(project)
    assert len(registry.tables) == 1
    assert registry.tables[0].name == "sales"


def test_register_table_without_contract_warns(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)
    _write_schema(project)

    table, warnings = register_table(
        project,
        name="sales",
        schema_path="schema.json",
    )

    assert table.contract_path == ""
    assert warnings == ["No contract path provided."]


def test_register_table_rejects_duplicate_name(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)
    _write_schema(project)

    register_table(project, name="sales", schema_path="schema.json")

    with pytest.raises(DuplicateTableError, match="sales"):
        register_table(project, name="sales", schema_path="schema.json")


def test_register_table_requires_existing_schema(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)

    with pytest.raises(FileNotFoundError, match="Schema file not found"):
        register_table(project, name="sales", schema_path="missing.json")
