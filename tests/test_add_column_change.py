"""Tests for add_column change validation."""

import pytest

from changeguard.changes import ChangeValidationError, validate_add_column
from changeguard.models import ChangeRequest, ChangeType


def _add_column_request(**overrides) -> ChangeRequest:
    data = {
        "change_type": ChangeType.ADD_COLUMN,
        "table": "sales",
        "column": "discount",
        "column_type": "float",
    }
    data.update(overrides)
    return ChangeRequest(**data)


def test_validate_add_column_accepts_valid_request() -> None:
    request = _add_column_request(nullable=False)

    validated = validate_add_column(request)

    assert validated.nullable is False


def test_validate_add_column_defaults_nullable_to_true() -> None:
    request = _add_column_request(nullable=None)

    validated = validate_add_column(request)

    assert validated.nullable is True


def test_validate_add_column_requires_column() -> None:
    request = _add_column_request(column="")

    with pytest.raises(ChangeValidationError, match="column is required"):
        validate_add_column(request)


def test_validate_add_column_requires_type() -> None:
    request = _add_column_request(column_type="")

    with pytest.raises(ChangeValidationError, match="type is required"):
        validate_add_column(request)


def test_validate_add_column_requires_table() -> None:
    request = _add_column_request(table="  ")

    with pytest.raises(ChangeValidationError, match="table is required"):
        validate_add_column(request)


def test_validate_add_column_rejects_wrong_change_type() -> None:
    request = ChangeRequest(
        change_type=ChangeType.DROP_COLUMN,
        table="sales",
        column="discount",
    )

    with pytest.raises(ChangeValidationError, match="add_column"):
        validate_add_column(request)
