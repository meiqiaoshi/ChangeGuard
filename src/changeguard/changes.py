"""Change request models and YAML loading."""

from pathlib import Path

import yaml

from changeguard.models import ChangeRequest, ChangeType


class ChangeValidationError(ValueError):
    """Raised when a change request fails validation."""


def validate_add_column(request: ChangeRequest) -> ChangeRequest:
    """Validate an add_column change request."""
    if request.change_type != ChangeType.ADD_COLUMN:
        raise ChangeValidationError("Expected add_column change type")

    if not request.table.strip():
        raise ChangeValidationError("table is required")

    if not request.column or not request.column.strip():
        raise ChangeValidationError("column is required")

    if not request.column_type or not request.column_type.strip():
        raise ChangeValidationError("type is required")

    nullable = True if request.nullable is None else request.nullable
    return request.model_copy(update={"nullable": nullable})


def validate_rename_column(request: ChangeRequest) -> ChangeRequest:
    """Validate a rename_column change request."""
    if request.change_type != ChangeType.RENAME_COLUMN:
        raise ChangeValidationError("Expected rename_column change type")

    if not request.table.strip():
        raise ChangeValidationError("table is required")

    if not request.column or not request.column.strip():
        raise ChangeValidationError("column is required")

    if not request.new_name or not request.new_name.strip():
        raise ChangeValidationError("new_name is required")

    if request.column.strip() == request.new_name.strip():
        raise ChangeValidationError("new_name must differ from column")

    return request


def _require_table_and_column(request: ChangeRequest) -> None:
    if not request.table.strip():
        raise ChangeValidationError("table is required")

    if not request.column or not request.column.strip():
        raise ChangeValidationError("column is required")


def validate_drop_column(request: ChangeRequest) -> ChangeRequest:
    """Validate a drop_column change request."""
    if request.change_type != ChangeType.DROP_COLUMN:
        raise ChangeValidationError("Expected drop_column change type")

    _require_table_and_column(request)
    return request


def validate_change_column_type(request: ChangeRequest) -> ChangeRequest:
    """Validate a change_column_type change request."""
    if request.change_type != ChangeType.CHANGE_COLUMN_TYPE:
        raise ChangeValidationError("Expected change_column_type change type")

    _require_table_and_column(request)

    if not request.new_type or not request.new_type.strip():
        raise ChangeValidationError("new_type is required")

    return request


def validate_set_nullable(request: ChangeRequest) -> ChangeRequest:
    """Validate a set_nullable change request."""
    if request.change_type != ChangeType.SET_NULLABLE:
        raise ChangeValidationError("Expected set_nullable change type")

    _require_table_and_column(request)

    if request.nullable is None:
        raise ChangeValidationError("nullable is required")

    return request


def load_change_request(path: Path) -> ChangeRequest:
    """Load a change request from a YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Change request file not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ChangeValidationError("Change request YAML must be a mapping")

    return ChangeRequest.model_validate(data)
