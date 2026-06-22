"""Review planner orchestrating the full change review pipeline."""

from pathlib import Path

from changeguard.contracts import check_change_against_contract, load_contract
from changeguard.models import ChangeRequest, CheckStatus, ReviewResult
from changeguard.registry import TableNotFoundError, get_table
from changeguard.rules import aggregate_decision, score_risk_level


def _load_contract_checks(base: Path, change_request: ChangeRequest):
    table = get_table(base, change_request.table)
    if not table.contract_path:
        return []

    contract_file = Path(table.contract_path)
    if not contract_file.is_absolute():
        contract_file = base / contract_file

    contract = load_contract(contract_file)
    return check_change_against_contract(contract, change_request)


def review_change(base: Path | None, change_request: ChangeRequest) -> ReviewResult:
    """Review a proposed change and return a structured review result."""
    project_base = base or Path.cwd()
    check_results = []

    try:
        check_results.extend(_load_contract_checks(project_base, change_request))
    except (TableNotFoundError, FileNotFoundError, ValueError):
        pass

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
