"""Decision aggregation and risk scoring rules."""

from changeguard.lineage import (
    check_drop_column_against_lineage,
    check_rename_column_against_lineage,
)
from changeguard.models import ChangeRequest, ChangeType, LineageGraph, CheckResult


def check_change_against_lineage(
    graph: LineageGraph,
    request: ChangeRequest,
) -> list[CheckResult]:
    """Run lineage checks for supported change request types."""
    if request.change_type == ChangeType.RENAME_COLUMN:
        return check_rename_column_against_lineage(graph, request)
    if request.change_type == ChangeType.DROP_COLUMN:
        return check_drop_column_against_lineage(graph, request)
    return []
