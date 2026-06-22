"""Tests for decision aggregation rules."""

from changeguard.models import CheckResult, CheckStatus, Decision
from changeguard.rules import aggregate_decision


def _check(status: CheckStatus) -> CheckResult:
    return CheckResult(
        name=f"check_{status.value.lower()}",
        status=status,
        message=f"example {status.value}",
    )


def test_aggregate_decision_returns_allow_when_all_pass() -> None:
    decision = aggregate_decision([_check(CheckStatus.PASS), _check(CheckStatus.PASS)])

    assert decision == Decision.ALLOW


def test_aggregate_decision_returns_warn_when_any_warn_and_no_fail() -> None:
    decision = aggregate_decision([_check(CheckStatus.PASS), _check(CheckStatus.WARN)])

    assert decision == Decision.WARN


def test_aggregate_decision_returns_block_when_any_fail() -> None:
    decision = aggregate_decision([_check(CheckStatus.WARN), _check(CheckStatus.FAIL)])

    assert decision == Decision.BLOCK


def test_aggregate_decision_returns_allow_for_empty_results() -> None:
    decision = aggregate_decision([])

    assert decision == Decision.ALLOW
