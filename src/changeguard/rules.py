"""Decision aggregation and risk scoring rules."""

from changeguard.lineage import (
    check_drop_column_against_lineage,
    check_rename_column_against_lineage,
)
from changeguard.models import (
    ChangeRequest,
    CheckStatus,
    CheckResult,
    Decision,
    ChangeType,
    LineageGraph,
)


def aggregate_decision(check_results: list[CheckResult]) -> Decision:
    """Aggregate individual check results into a final decision."""
    if any(result.status == CheckStatus.FAIL for result in check_results):
        return Decision.BLOCK
    if any(result.status == CheckStatus.WARN for result in check_results):
        return Decision.WARN
    return Decision.ALLOW


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
