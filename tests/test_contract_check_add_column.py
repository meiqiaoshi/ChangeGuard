"""Tests for add_column contract checks."""

from pathlib import Path

from changeguard.changes import validate_add_column
from changeguard.contracts import check_add_column_against_contract, load_contract
from changeguard.models import ChangeRequest, ChangeType, CheckStatus

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "contracts"


def _add_column_request(**overrides) -> ChangeRequest:
    data = {
        "change_type": ChangeType.ADD_COLUMN,
        "table": "sales",
        "column": "discount",
        "column_type": "float",
    }
    data.update(overrides)
    return validate_add_column(ChangeRequest(**data))


def test_check_add_column_allows_nullable_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _add_column_request(nullable=True)

    results = check_add_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.PASS
    assert results[0].source == "contract"


def test_check_add_column_warns_on_required_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _add_column_request(nullable=False)

    results = check_add_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN
    assert "required column" in results[0].message


def test_check_add_column_blocks_duplicate_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")
    request = _add_column_request(column="amount", nullable=True)

    results = check_add_column_against_contract(contract, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
    assert "already exists" in results[0].message
