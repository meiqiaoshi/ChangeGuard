"""Tests for rename_column contract checks."""

from pathlib import Path

from changeguard.changes import validate_rename_column
from changeguard.contracts import check_rename_column_against_contract, load_contract
from changeguard.models import ChangeRequest, ChangeType, CheckStatus

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "contracts"


def _rename_column_request(**overrides) -> ChangeRequest:
    data = {
        "change_type": ChangeType.RENAME_COLUMN,
        "table": "sales",
        "column": "amount",
        "new_name": "order_amount",
    }
    data.update(overrides)
    return validate_rename_column(ChangeRequest(**data))


def test_check_rename_column_blocks_required_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _rename_column_request(column="amount", new_name="order_amount")

    results = check_rename_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
    assert "required by contract" in results[0].message


def test_check_rename_column_warns_on_optional_contract_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _rename_column_request(column="status", new_name="order_status")

    results = check_rename_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN
    assert "defined in contract" in results[0].message


def test_check_rename_column_warns_when_old_column_not_in_contract() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _rename_column_request(column="legacy_flag", new_name="legacy_status")

    results = check_rename_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN
    assert "not defined in contract" in results[0].message


def test_check_rename_column_blocks_when_new_name_exists() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _rename_column_request(column="status", new_name="amount")

    results = check_rename_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
    assert "already exists" in results[0].message
