"""Data contract loading and validation checks."""

from pathlib import Path

import yaml

from changeguard.models import Contract, ContractColumn


class ContractLoadError(ValueError):
    """Raised when a contract file cannot be loaded."""


def load_contract(path: Path) -> Contract:
    """Load a data contract from a YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Contract file not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContractLoadError("Contract YAML must be a mapping")

    return Contract.model_validate(data)


def get_contract_column(contract: Contract, column_name: str) -> ContractColumn | None:
    """Return contract metadata for a column, if present."""
    return contract.columns.get(column_name)


def has_contract_column(contract: Contract, column_name: str) -> bool:
    """Return whether a column is defined in the contract."""
    return column_name in contract.columns


def is_required_column(contract: Contract, column_name: str) -> bool:
    """Return whether a contract column is required."""
    column = get_contract_column(contract, column_name)
    if column is None:
        return False
    if column.required:
        return True
    return column.nullable is False
