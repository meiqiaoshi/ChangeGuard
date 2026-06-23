"""Review planner orchestrating the full change review pipeline."""

from pathlib import Path

from changeguard.contracts import check_change_against_contract, load_contract
from changeguard.lineage import find_column_impact, load_lineage
from changeguard.models import ChangeRequest, ChangeType, CheckStatus, ReviewResult
from changeguard.registry import TableNotFoundError, get_table
from changeguard.rules import aggregate_decision, check_change_against_lineage, score_risk_level


def _load_contract_checks(base: Path, change_request: ChangeRequest):
    table = get_table(base, change_request.table)
    if not table.contract_path:
        return []

    contract_file = Path(table.contract_path)
    if not contract_file.is_absolute():
        contract_file = base / contract_file

    contract = load_contract(contract_file)
    return check_change_against_contract(contract, change_request)


def _load_lineage_checks(base: Path, change_request: ChangeRequest):
    table = get_table(base, change_request.table)
    if not table.lineage_path:
        return [], []

    lineage_file = Path(table.lineage_path)
    if not lineage_file.is_absolute():
        lineage_file = base / lineage_file

    graph = load_lineage(lineage_file)
    check_results = check_change_against_lineage(graph, change_request)

    impacted_assets: list[str] = []
    if (
        change_request.column
        and change_request.change_type in (ChangeType.RENAME_COLUMN, ChangeType.DROP_COLUMN)
    ):
        reference = f"{change_request.table}.{change_request.column}"
        impacted_assets = [
            (
                f"{impact.asset.name}.{impact.target_column}"
                if impact.target_column
                else impact.asset.name
            )
            for impact in find_column_impact(graph, reference)
        ]

    return check_results, impacted_assets


def review_change(base: Path | None, change_request: ChangeRequest) -> ReviewResult:
    """Review a proposed change and return a structured review result."""
    project_base = base or Path.cwd()
    check_results = []
    impacted_assets: list[str] = []

    try:
        check_results.extend(_load_contract_checks(project_base, change_request))
    except (TableNotFoundError, FileNotFoundError, ValueError):
        pass

    try:
        lineage_checks, lineage_impacts = _load_lineage_checks(project_base, change_request)
        check_results.extend(lineage_checks)
        impacted_assets.extend(lineage_impacts)
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
        impacted_assets=impacted_assets,
    )
