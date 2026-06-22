"""Data contract loading and validation checks."""

from pathlib import Path

import yaml

from changeguard.models import (
    ChangeRequest,
    ChangeType,
    CheckResult,
    CheckStatus,
    Contract,
    ContractColumn,
)


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


def _is_nullable_in_contract(contract: Contract, column_name: str) -> bool:
    column = get_contract_column(contract, column_name)
    if column is None:
        return True
    if column.nullable is not None:
        return column.nullable
    return not column.required


def check_change_column_type_against_contract(
    contract: Contract,
    request: ChangeRequest,
) -> list[CheckResult]:
    """Check a change_column_type change request against a data contract."""
    if request.column is None or request.new_type is None:
        raise ValueError("change_column_type change request requires column and new_type")

    column_name = request.column

    if not has_contract_column(contract, column_name):
        return [
            CheckResult(
                name="contract_type_change_unknown_column",
                status=CheckStatus.WARN,
                message=(
                    f"Column {column_name} is not defined in contract for table "
                    f"{contract.table}"
                ),
            )
        ]

    contract_column = get_contract_column(contract, column_name)
    assert contract_column is not None

    if contract_column.type == request.new_type:
        return [
            CheckResult(
                name="contract_type_unchanged",
                status=CheckStatus.PASS,
                message=(
                    f"Column {column_name} already has type {request.new_type} in contract"
                ),
            )
        ]

    return [
        CheckResult(
            name="contract_type_change",
            status=CheckStatus.FAIL,
            message=(
                f"Changing type of contract column {column_name} from "
                f"{contract_column.type} to {request.new_type} is not allowed"
            ),
        )
    ]


def check_set_nullable_against_contract(
    contract: Contract,
    request: ChangeRequest,
) -> list[CheckResult]:
    """Check a set_nullable change request against a data contract."""
    if request.column is None or request.nullable is None:
        raise ValueError("set_nullable change request requires column and nullable")

    column_name = request.column

    if not has_contract_column(contract, column_name):
        return [
            CheckResult(
                name="contract_nullability_unknown_column",
                status=CheckStatus.WARN,
                message=(
                    f"Column {column_name} is not defined in contract for table "
                    f"{contract.table}"
                ),
            )
        ]

    currently_nullable = _is_nullable_in_contract(contract, column_name)

    if currently_nullable and not request.nullable:
        return [
            CheckResult(
                name="contract_tighten_nullability",
                status=CheckStatus.FAIL,
                message=(
                    f"Tightening nullability for contract column {column_name} is not "
                    "allowed without validation"
                ),
            )
        ]

    if not currently_nullable and request.nullable:
        return [
            CheckResult(
                name="contract_relax_nullability",
                status=CheckStatus.WARN,
                message=(
                    f"Relaxing nullability for required contract column {column_name} "
                    "weakens published guarantees"
                ),
            )
        ]

    return [
        CheckResult(
            name="contract_nullability_unchanged",
            status=CheckStatus.PASS,
            message=f"Nullability for contract column {column_name} is unchanged",
        )
    ]


def check_change_against_contract(
    contract: Contract,
    request: ChangeRequest,
) -> list[CheckResult]:
    """Run contract checks for supported change request types."""
    if request.change_type == ChangeType.ADD_COLUMN:
        return check_add_column_against_contract(contract, request)
    if request.change_type == ChangeType.RENAME_COLUMN:
        return check_rename_column_against_contract(contract, request)
    if request.change_type == ChangeType.DROP_COLUMN:
        return check_drop_column_against_contract(contract, request)
    if request.change_type == ChangeType.CHANGE_COLUMN_TYPE:
        return check_change_column_type_against_contract(contract, request)
    if request.change_type == ChangeType.SET_NULLABLE:
        return check_set_nullable_against_contract(contract, request)
    return []
