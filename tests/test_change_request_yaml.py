"""Tests for loading change requests from YAML."""

from pathlib import Path

import pytest

from changeguard.changes import ChangeValidationError, load_change_request
from changeguard.models import ChangeType

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "change_requests"


def test_load_add_column_change_request_from_yaml() -> None:
    request = load_change_request(EXAMPLES_DIR / "add_discount_column.yml")

    assert request.change_type == ChangeType.ADD_COLUMN
    assert request.table == "sales"
    assert request.column == "discount"
    assert request.column_type == "float"
    assert request.nullable is True
    assert request.description == "Add promotional discount column for pricing experiments"


def test_load_rename_column_change_request_from_yaml() -> None:
    request = load_change_request(EXAMPLES_DIR / "rename_amount_column.yml")

    assert request.change_type == ChangeType.RENAME_COLUMN
    assert request.table == "sales"
    assert request.column == "amount"
    assert request.new_name == "order_amount"


def test_load_drop_column_change_request_from_yaml() -> None:
    request = load_change_request(EXAMPLES_DIR / "drop_customer_id.yml")

    assert request.change_type == ChangeType.DROP_COLUMN
    assert request.table == "sales"
    assert request.column == "customer_id"


def test_load_change_request_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yml"

    with pytest.raises(FileNotFoundError, match="Change request file not found"):
        load_change_request(missing)


def test_load_change_request_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yml"
    path.write_text("- not-a-mapping\n", encoding="utf-8")

    with pytest.raises(ChangeValidationError, match="mapping"):
        load_change_request(path)
