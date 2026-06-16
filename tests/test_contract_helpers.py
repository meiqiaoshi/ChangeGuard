"""Tests for contract column lookup helpers."""

from pathlib import Path

from changeguard.contracts import (
    get_contract_column,
    has_contract_column,
    is_required_column,
    load_contract,
)

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "contracts"


def test_get_contract_column_returns_existing_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")

    column = get_contract_column(contract, "amount")

    assert column is not None
    assert column.type == "float"
    assert column.required is True


def test_get_contract_column_returns_none_for_missing_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")

    assert get_contract_column(contract, "missing_column") is None


def test_has_contract_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")

    assert has_contract_column(contract, "customer_id") is True
    assert has_contract_column(contract, "missing_column") is False


def test_is_required_column() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")

    assert is_required_column(contract, "amount") is True
    assert is_required_column(contract, "status") is False
    assert is_required_column(contract, "missing_column") is False
