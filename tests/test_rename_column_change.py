"""Tests for rename_column change validation."""

import pytest

from changeguard.changes import ChangeValidationError, validate_rename_column
from changeguard.models import ChangeRequest, ChangeType


def _rename_column_request(**overrides) -> ChangeRequest:
    data = {
        "change_type": ChangeType.RENAME_COLUMN,
        "table": "sales",
        "column": "amount",
        "new_name": "order_amount",
    }
    data.update(overrides)
    return ChangeRequest(**data)


def test_validate_rename_column_accepts_valid_request() -> None:
    request = _rename_column_request()

    validated = validate_rename_column(request)

    assert validated.column == "amount"
    assert validated.new_name == "order_amount"


def test_validate_rename_column_rejects_same_name() -> None:
    request = _rename_column_request(new_name="amount")

    with pytest.raises(ChangeValidationError, match="must differ"):
        validate_rename_column(request)


def test_validate_rename_column_requires_new_name() -> None:
    request = _rename_column_request(new_name="")

    with pytest.raises(ChangeValidationError, match="new_name is required"):
        validate_rename_column(request)


def test_validate_rename_column_requires_column() -> None:
    request = _rename_column_request(column="")

    with pytest.raises(ChangeValidationError, match="column is required"):
        validate_rename_column(request)


def test_validate_rename_column_requires_table() -> None:
    request = _rename_column_request(table="  ")

    with pytest.raises(ChangeValidationError, match="table is required"):
        validate_rename_column(request)


def test_validate_rename_column_rejects_wrong_change_type() -> None:
    request = ChangeRequest(
        change_type=ChangeType.ADD_COLUMN,
        table="sales",
        column="amount",
        column_type="float",
    )

    with pytest.raises(ChangeValidationError, match="rename_column"):
        validate_rename_column(request)
