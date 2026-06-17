"""Tests for drop_column contract checks."""

from pathlib import Path

from changeguard.changes import validate_drop_column
from changeguard.contracts import check_drop_column_against_contract, load_contract
from changeguard.models import ChangeRequest, ChangeType, CheckStatus

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "contracts"


def _drop_column_request(**overrides) -> ChangeRequest:
    data = {
        "change_type": ChangeType.DROP_COLUMN,
        "table": "sales",
        "column": "customer_id",
    }
    data.update(overrides)
    return validate_drop_column(ChangeRequest(**data))


def test_check_drop_column_blocks_required_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _drop_column_request(column="customer_id")

    results = check_drop_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
    assert "required by contract" in results[0].message


def test_check_drop_column_warns_on_optional_contract_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _drop_column_request(column="status")

    results = check_drop_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN
    assert "defined in contract" in results[0].message


def test_check_drop_column_warns_when_column_not_in_contract() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _drop_column_request(column="legacy_flag")

    results = check_drop_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN
    assert "not defined in contract" in results[0].message
