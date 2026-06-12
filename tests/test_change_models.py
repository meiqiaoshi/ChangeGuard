"""Tests for change request models."""

from changeguard.models import ChangeRequest, ChangeType


def test_add_column_change_request() -> None:
    request = ChangeRequest(
        change_type=ChangeType.ADD_COLUMN,
        table="sales",
        column="discount",
        column_type="float",
        nullable=True,
        description="Add promotional discount column",
    )

    assert request.change_type == ChangeType.ADD_COLUMN
    assert request.table == "sales"
    assert request.column == "discount"
    assert request.column_type == "float"
    assert request.nullable is True


def test_rename_column_change_request() -> None:
    request = ChangeRequest(
        change_type=ChangeType.RENAME_COLUMN,
        table="sales",
        column="amount",
        new_name="order_amount",
    )

    assert request.change_type == ChangeType.RENAME_COLUMN
    assert request.new_name == "order_amount"


def test_drop_column_change_request() -> None:
    request = ChangeRequest(
        change_type=ChangeType.DROP_COLUMN,
        table="sales",
        column="legacy_flag",
    )

    assert request.change_type == ChangeType.DROP_COLUMN
    assert request.column == "legacy_flag"


def test_change_column_type_request() -> None:
    request = ChangeRequest(
        change_type=ChangeType.CHANGE_COLUMN_TYPE,
        table="sales",
        column="quantity",
        new_type="bigint",
    )

    assert request.change_type == ChangeType.CHANGE_COLUMN_TYPE
    assert request.new_type == "bigint"


def test_set_nullable_change_request() -> None:
    request = ChangeRequest(
        change_type=ChangeType.SET_NULLABLE,
        table="sales",
        column="customer_id",
        nullable=False,
    )

    assert request.change_type == ChangeType.SET_NULLABLE
    assert request.nullable is False


def test_change_request_accepts_type_alias() -> None:
    request = ChangeRequest.model_validate(
        {
            "change_type": "add_column",
            "table": "sales",
            "column": "discount",
            "type": "float",
            "nullable": True,
        }
    )

    assert request.column_type == "float"
