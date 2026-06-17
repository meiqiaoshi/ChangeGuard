"""Tests for change_column_type and set_nullable contract checks."""

from pathlib import Path

from changeguard.changes import validate_change_column_type, validate_set_nullable
from changeguard.contracts import (
    check_change_column_type_against_contract,
    check_set_nullable_against_contract,
    load_contract,
)
from changeguard.models import ChangeRequest, ChangeType, CheckStatus

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "contracts"


def test_check_change_column_type_blocks_contract_column_type_change() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = validate_change_column_type(
        ChangeRequest(
            change_type=ChangeType.CHANGE_COLUMN_TYPE,
            table="sales",
            column="amount",
            new_type="int",
        )
    )

    results = check_change_column_type_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
    assert "not allowed" in results[0].message


def test_check_change_column_type_warns_for_unknown_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = validate_change_column_type(
        ChangeRequest(
            change_type=ChangeType.CHANGE_COLUMN_TYPE,
            table="sales",
            column="legacy_flag",
            new_type="string",
        )
    )

    results = check_change_column_type_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN
    assert "not defined in contract" in results[0].message


def test_check_set_nullable_blocks_tightening_nullability() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = validate_set_nullable(
        ChangeRequest(
            change_type=ChangeType.SET_NULLABLE,
            table="sales",
            column="status",
            nullable=False,
        )
    )

    results = check_set_nullable_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
    assert "Tightening nullability" in results[0].message


def test_check_set_nullable_warns_when_relaxing_required_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = validate_set_nullable(
        ChangeRequest(
            change_type=ChangeType.SET_NULLABLE,
            table="sales",
            column="customer_id",
            nullable=True,
        )
    )

    results = check_set_nullable_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN
    assert "Relaxing nullability" in results[0].message
