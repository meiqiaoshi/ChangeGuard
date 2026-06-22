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
    RiskLevel,
)


def aggregate_decision(check_results: list[CheckResult]) -> Decision:
    """Aggregate individual check results into a final decision."""
    if any(result.status == CheckStatus.FAIL for result in check_results):
        return Decision.BLOCK
    if any(result.status == CheckStatus.WARN for result in check_results):
        return Decision.WARN
    return Decision.ALLOW


def _has_dashboard_impact(check_results: list[CheckResult]) -> bool:
    for result in check_results:
        if result.status != CheckStatus.FAIL:
            continue
        if "dashboard" in result.message.lower():
            return True
    return False


def score_risk_level(
    decision: Decision,
    check_results: list[CheckResult],
    change_request: ChangeRequest | None = None,
) -> RiskLevel:
    """Assign a risk level based on the decision and check results."""
    if decision == Decision.BLOCK:
        if _has_dashboard_impact(check_results):
            return RiskLevel.CRITICAL
        return RiskLevel.HIGH

    if decision == Decision.WARN:
        return RiskLevel.MEDIUM

    if (
        change_request is not None
        and change_request.change_type == ChangeType.ADD_COLUMN
        and change_request.nullable
    ):
        return RiskLevel.LOW

    return RiskLevel.LOW


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
