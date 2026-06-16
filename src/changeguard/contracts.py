"""Data contract loading and validation checks."""

from pathlib import Path

import yaml

from changeguard.models import Contract


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
