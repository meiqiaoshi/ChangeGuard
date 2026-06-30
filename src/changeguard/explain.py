"""Deterministic explanations for completed change reviews."""

from changeguard.models import Decision, ReviewResult


def explain_review(review_result: ReviewResult) -> str:
    """Generate a deterministic narrative explanation for a review result.

    The explanation summarizes the rule-engine output. It does not change
    the decision or risk level.
    """
    decision = review_result.decision.value
    risk = review_result.risk_level.value
    lines = [
        f"This change received a {decision} decision with {risk} risk.",
        _decision_summary(review_result),
    ]

    if review_result.reasons:
        lines.extend(["", "Key concerns:"])
        lines.extend(f"- {reason}" for reason in review_result.reasons)

    if review_result.impacted_assets:
        lines.extend(["", "Impacted downstream assets:"])
        lines.extend(f"- {asset}" for asset in review_result.impacted_assets)

    if review_result.migration_plan and review_result.migration_plan.steps:
        lines.extend(["", "Recommended migration approach:"])
        for step in review_result.migration_plan.steps:
            lines.append(f"{step.step_number}. {step.title}")

    if review_result.rollback_notes:
        lines.extend(["", "Rollback guidance:"])
        lines.extend(f"- {note}" for note in review_result.rollback_notes)

    return "\n".join(lines)


def _decision_summary(review_result: ReviewResult) -> str:
    if review_result.decision == Decision.ALLOW:
        return "The proposed change passed all safety checks and may proceed with normal deployment practices."
    if review_result.decision == Decision.WARN:
        return (
            "The proposed change has warnings that should be reviewed before applying it in production."
        )
    return (
        "The proposed change failed one or more safety checks and should not be applied as requested."
    )
