"""Tests for table registry metadata models."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from changeguard.models import TableMetadata


def _sample_table(**overrides) -> TableMetadata:
    now = datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc)
    data = {
        "name": "sales",
        "schema_path": "examples/schemas/sales_schema.json",
        "contract_path": "examples/contracts/sales_contract.yml",
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return TableMetadata(**data)


def test_table_metadata_required_fields() -> None:
    table = _sample_table()

    assert table.name == "sales"
    assert table.schema_path == "examples/schemas/sales_schema.json"
    assert table.contract_path == "examples/contracts/sales_contract.yml"
    assert table.lineage_path is None
    assert table.owner is None
    assert table.description is None
    assert table.tags == []


def test_table_metadata_optional_fields() -> None:
    table = _sample_table(
        lineage_path="examples/lineage/sample_lineage.yml",
        owner="analytics-team",
        description="Core sales fact table",
        tags=["fact", "core"],
    )

    assert table.lineage_path == "examples/lineage/sample_lineage.yml"
    assert table.owner == "analytics-team"
    assert table.description == "Core sales fact table"
    assert table.tags == ["fact", "core"]


def test_table_metadata_serialization_round_trip() -> None:
    table = _sample_table(
        lineage_path="examples/lineage/sample_lineage.yml",
        tags=["fact"],
    )

    payload = table.model_dump(mode="json")
    restored = TableMetadata.model_validate(payload)

    assert restored == table


def test_table_metadata_missing_required_field_raises() -> None:
    now = datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(ValidationError):
        TableMetadata(
            name="sales",
            schema_path="examples/schemas/sales_schema.json",
            created_at=now,
            updated_at=now,
        )
