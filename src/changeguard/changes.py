"""Change request models and YAML loading."""

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
