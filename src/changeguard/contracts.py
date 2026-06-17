"""Data contract loading and validation checks."""

from pathlib import Path

import yaml

from changeguard.models import ChangeRequest, CheckResult, CheckStatus, Contract, ContractColumn


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


def check_add_column_against_contract(
    contract: Contract,
    request: ChangeRequest,
) -> list[CheckResult]:
    """Check an add_column change request against a data contract."""
    if request.column is None:
        raise ValueError("add_column change request requires a column")

    column_name = request.column

    if has_contract_column(contract, column_name):
        return [
            CheckResult(
                name="contract_column_exists",
                status=CheckStatus.FAIL,
                message=(
                    f"Column {column_name} already exists in contract for table "
                    f"{contract.table}"
                ),
            )
        ]

    if request.nullable:
        return [
            CheckResult(
                name="contract_add_nullable_column",
                status=CheckStatus.PASS,
                message=(
                    f"Adding nullable column {column_name} is allowed by contract"
                ),
            )
        ]

    return [
        CheckResult(
            name="contract_add_required_column",
            status=CheckStatus.WARN,
            message=(
                f"Adding required column {column_name} without default may violate "
                "existing rows"
            ),
        )
    ]


def check_rename_column_against_contract(
    contract: Contract,
    request: ChangeRequest,
) -> list[CheckResult]:
    """Check a rename_column change request against a data contract."""
    if request.column is None or request.new_name is None:
        raise ValueError("rename_column change request requires column and new_name")

    old_name = request.column
    new_name = request.new_name
    results: list[CheckResult] = []

    if has_contract_column(contract, new_name):
        results.append(
            CheckResult(
                name="contract_new_column_exists",
                status=CheckStatus.FAIL,
                message=(
                    f"Column {new_name} already exists in contract for table "
                    f"{contract.table}"
                ),
            )
        )
        return results

    if not has_contract_column(contract, old_name):
        results.append(
            CheckResult(
                name="contract_rename_unknown_column",
                status=CheckStatus.WARN,
                message=(
                    f"Column {old_name} is not defined in contract for table "
                    f"{contract.table}"
                ),
            )
        )
        return results

    if is_required_column(contract, old_name):
        results.append(
            CheckResult(
                name="contract_rename_required_column",
                status=CheckStatus.FAIL,
                message=(
                    f"Column {old_name} is required by contract for table "
                    f"{contract.table}"
                ),
            )
        )
        return results

    results.append(
        CheckResult(
            name="contract_rename_defined_column",
            status=CheckStatus.WARN,
            message=(
                f"Column {old_name} is defined in contract for table {contract.table}"
            ),
        )
    )
    return results


def check_drop_column_against_contract(
    contract: Contract,
    request: ChangeRequest,
) -> list[CheckResult]:
    """Check a drop_column change request against a data contract."""
    if request.column is None:
        raise ValueError("drop_column change request requires a column")

    column_name = request.column

    if not has_contract_column(contract, column_name):
        return [
            CheckResult(
                name="contract_drop_unknown_column",
                status=CheckStatus.WARN,
                message=(
                    f"Column {column_name} is not defined in contract for table "
                    f"{contract.table}"
                ),
            )
        ]

    if is_required_column(contract, column_name):
        return [
            CheckResult(
                name="contract_drop_required_column",
                status=CheckStatus.FAIL,
                message=(
                    f"Column {column_name} is required by contract for table "
                    f"{contract.table}"
                ),
            )
        ]

    return [
        CheckResult(
            name="contract_drop_optional_column",
            status=CheckStatus.WARN,
            message=(
                f"Column {column_name} is defined in contract for table "
                f"{contract.table} and should be reviewed before dropping"
            ),
        )
    ]


def check_drop_column_against_contract(
    contract: Contract,
    request: ChangeRequest,
) -> list[CheckResult]:
    """Check a drop_column change request against a data contract."""
    if request.column is None:
        raise ValueError("drop_column change request requires a column")

    column_name = request.column

    if not has_contract_column(contract, column_name):
        return [
            CheckResult(
                name="contract_drop_unknown_column",
                status=CheckStatus.WARN,
                message=(
                    f"Column {column_name} is not defined in contract for table "
                    f"{contract.table}"
                ),
            )
        ]

    if is_required_column(contract, column_name):
        return [
            CheckResult(
                name="contract_drop_required_column",
                status=CheckStatus.FAIL,
                message=(
                    f"Column {column_name} is required by contract for table "
                    f"{contract.table}"
                ),
            )
        ]

    return [
        CheckResult(
            name="contract_drop_optional_column",
            status=CheckStatus.WARN,
            message=(
                f"Column {column_name} is defined in contract for table "
                f"{contract.table} and should be reviewed before dropping"
            ),
        )
    ]
