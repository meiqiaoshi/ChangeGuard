"""Review planner orchestrating the full change review pipeline."""

from pathlib import Path

from changeguard.models import (
    ChangeRequest,
    CheckResult,
    CheckStatus,
    ReviewResult,
)
from changeguard.rules import aggregate_decision, score_risk_level


def review_change(base: Path | None, change_request: ChangeRequest) -> ReviewResult:
    """Review a proposed change and return a structured review result."""
    _ = base
    check_results = [
        CheckResult(
            name="planner_placeholder",
            status=CheckStatus.PASS,
            message=(
                f"Received {change_request.change_type.value} change for table "
                f"{change_request.table}"
            ),
            source="planner",
        )
    ]

    decision = aggregate_decision(check_results)
    risk_level = score_risk_level(decision, check_results, change_request)
    reasons = [
        result.message
        for result in check_results
        if result.status in (CheckStatus.WARN, CheckStatus.FAIL)
    ]

    return ReviewResult(
        decision=decision,
        risk_level=risk_level,
        reasons=reasons,
        check_results=check_results,
        impacted_assets=[],
    )
