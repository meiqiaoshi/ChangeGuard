"""Tests for drop_column, change_column_type, and set_nullable validation."""

import pytest

from changeguard.changes import (
    ChangeValidationError,
    validate_change_column_type,
    validate_drop_column,
    validate_set_nullable,
)
from changeguard.models import ChangeRequest, ChangeType


def test_validate_drop_column_accepts_valid_request() -> None:
    request = ChangeRequest(
        change_type=ChangeType.DROP_COLUMN,
        table="sales",
        column="legacy_flag",
    )

    validated = validate_drop_column(request)

    assert validated.column == "legacy_flag"


def test_validate_drop_column_requires_column() -> None:
    request = ChangeRequest(
        change_type=ChangeType.DROP_COLUMN,
        table="sales",
        column="",
    )

    with pytest.raises(ChangeValidationError, match="column is required"):
        validate_drop_column(request)


def test_validate_change_column_type_accepts_valid_request() -> None:
    request = ChangeRequest(
        change_type=ChangeType.CHANGE_COLUMN_TYPE,
        table="sales",
        column="quantity",
        new_type="bigint",
    )

    validated = validate_change_column_type(request)

    assert validated.new_type == "bigint"


def test_validate_change_column_type_requires_new_type() -> None:
    request = ChangeRequest(
        change_type=ChangeType.CHANGE_COLUMN_TYPE,
        table="sales",
        column="quantity",
        new_type="",
    )

    with pytest.raises(ChangeValidationError, match="new_type is required"):
        validate_change_column_type(request)


def test_validate_set_nullable_accepts_valid_request() -> None:
    request = ChangeRequest(
        change_type=ChangeType.SET_NULLABLE,
        table="sales",
        column="customer_id",
        nullable=False,
    )

    validated = validate_set_nullable(request)

    assert validated.nullable is False


def test_validate_set_nullable_requires_nullable() -> None:
    request = ChangeRequest(
        change_type=ChangeType.SET_NULLABLE,
        table="sales",
        column="customer_id",
        nullable=None,
    )

    with pytest.raises(ChangeValidationError, match="nullable is required"):
        validate_set_nullable(request)


def test_validate_drop_column_requires_table() -> None:
    request = ChangeRequest(
        change_type=ChangeType.DROP_COLUMN,
        table="  ",
        column="legacy_flag",
    )

    with pytest.raises(ChangeValidationError, match="table is required"):
        validate_drop_column(request)
