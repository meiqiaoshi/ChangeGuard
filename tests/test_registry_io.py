"""Tests for registry load and save."""

from datetime import datetime, timezone
from pathlib import Path

from changeguard.models import TableMetadata
from changeguard.registry import Registry, load_registry, save_registry
from changeguard.workspace import init_workspace, registry_path


def _sample_table(name: str = "sales") -> TableMetadata:
    now = datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc)
    return TableMetadata(
        name=name,
        schema_path="examples/schemas/sales_schema.json",
        contract_path="examples/contracts/sales_contract.yml",
        lineage_path="examples/lineage/sample_lineage.yml",
        owner="analytics-team",
        description="Core sales fact table",
        tags=["fact"],
        created_at=now,
        updated_at=now,
    )


def test_load_registry_returns_empty_when_file_missing(tmp_path: Path) -> None:
    registry = load_registry(tmp_path)

    assert registry.tables == []


def test_save_and_load_registry_round_trip(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    original = Registry(tables=[_sample_table(), _sample_table("customers")])

    save_registry(tmp_path, original)
    loaded = load_registry(tmp_path)

    assert loaded == original


def test_save_registry_writes_json_file(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    registry = Registry(tables=[_sample_table()])

    save_registry(tmp_path, registry)

    assert registry_path(tmp_path).is_file()
    loaded = load_registry(tmp_path)
    assert loaded.tables[0].name == "sales"
