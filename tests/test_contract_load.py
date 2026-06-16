"""Tests for loading data contracts from YAML."""

from pathlib import Path

import pytest

from changeguard.contracts import ContractLoadError, load_contract

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "contracts"


def test_load_sales_contract_from_yaml() -> None:
    contract = load_contract(EXAMPLES_DIR / "sales_contract.yml")

    assert contract.table == "sales"
    assert contract.version == "1.0"
    assert contract.owner == "analytics-team"
    assert contract.columns["amount"].type == "float"
    assert contract.columns["amount"].required is True
    assert contract.columns["status"].required is False
    assert len(contract.rules) == 2
    assert contract.rules[0].name == "amount_non_negative"
    assert contract.rules[1].column == "amount"


def test_load_contract_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yml"

    with pytest.raises(FileNotFoundError, match="Contract file not found"):
        load_contract(missing)


def test_load_contract_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yml"
    path.write_text("- not-a-mapping\n", encoding="utf-8")

    with pytest.raises(ContractLoadError, match="mapping"):
        load_contract(path)
