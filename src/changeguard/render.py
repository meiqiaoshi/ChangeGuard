"""CLI-friendly review result rendering."""

from changeguard.audit import ReviewRunSummary
from changeguard.lineage import ColumnImpact
from changeguard.models import (
    AssetRef,
    ChangeRequest,
    CheckResult,
    CheckStatus,
    Contract,
    MigrationPlan,
    ReviewResult,
    TableMetadata,
)


def _render_section(title: str, body_lines: list[str]) -> str:
    if not body_lines:
        body_lines = ["(none)"]
    return "\n".join([title, *body_lines])


def render_table_list(tables: list[TableMetadata]) -> str:
    """Render a list of registered table names."""
    if not tables:
        return "No tables registered."
    return "\n".join(table.name for table in tables)


def render_runs_list(runs: list[ReviewRunSummary]) -> str:
    """Render a tabular list of saved review runs."""
    if not runs:
        return "No review runs saved."

    lines = ["run_id\tdecision\trisk_level\tchange_type\ttarget\tcreated_at"]
    for run in runs:
        lines.append(
            f"{run.run_id}\t{run.decision}\t{run.risk_level}\t"
            f"{run.change_type}\t{run.target}\t{run.created_at}"
        )
    return "\n".join(lines)


def render_table_inspection(table: TableMetadata) -> str:
    """Render detailed metadata for a registered table."""
    tags = ", ".join(table.tags) if table.tags else "(none)"
    owner = table.owner or "(none)"
    description = table.description or "(none)"
    contract_path = table.contract_path or "(none)"

    return "\n".join(
        [
            f"name: {table.name}",
            f"schema path: {table.schema_path}",
            f"contract path: {contract_path}",
            f"owner: {owner}",
            f"tags: {tags}",
            f"description: {description}",
        ]
    )


def render_change_request(request: ChangeRequest) -> str:
    """Render parsed change request details for CLI output."""
    lines = [
        f"change_type: {request.change_type.value}",
        f"table: {request.table}",
    ]

    if request.column is not None:
        lines.append(f"column: {request.column}")
    if request.new_name is not None:
        lines.append(f"new_name: {request.new_name}")
    if request.column_type is not None:
        lines.append(f"type: {request.column_type}")
    if request.new_type is not None:
        lines.append(f"new_type: {request.new_type}")
    if request.nullable is not None:
        lines.append(f"nullable: {str(request.nullable).lower()}")
    if request.description is not None:
        lines.append(f"description: {request.description}")
    if request.requested_by is not None:
        lines.append(f"requested_by: {request.requested_by}")

    return _render_section("Change Request", lines)


def render_contract_summary(contract: Contract) -> str:
    """Render a summary of a loaded data contract."""
    required_columns = [
        name
        for name, column in contract.columns.items()
        if column.required or column.nullable is False
    ]
    owner = contract.owner or "(none)"
    description = contract.description or "(none)"

    return "\n".join(
        [
            f"table: {contract.table}",
            f"version: {contract.version}",
            f"owner: {owner}",
            f"description: {description}",
            f"columns: {len(contract.columns)}",
            f"required columns: {', '.join(required_columns) or '(none)'}",
            f"rules: {len(contract.rules)}",
        ]
    )


def render_downstream_impact_list(reference: str, assets: list[AssetRef]) -> str:
    """Render downstream assets impacted by a table reference."""
    if not assets:
        return f"No downstream assets impacted by {reference}."

    lines = [f"Impacted assets for {reference}:"]
    for asset in assets:
        lines.append(f"- {asset.name} ({asset.asset_type.value})")
    return "\n".join(lines)


def render_column_impact_list(reference: str, impacts: list[ColumnImpact]) -> str:
    """Render downstream assets impacted by a column reference."""
    if not impacts:
        return f"No downstream assets impacted by {reference}."

    lines = [f"Impacted assets for {reference}:"]
    for impact in impacts:
        if impact.target_column:
            lines.append(
                f"- {impact.asset.name} ({impact.asset.asset_type.value}) "
                f"column: {impact.target_column}"
            )
        else:
            lines.append(f"- {impact.asset.name} ({impact.asset.asset_type.value})")
    return "\n".join(lines)


def render_lineage_check_results(results: list[CheckResult]) -> str:
    """Render lineage check results for propose output."""
    lines = ["Lineage checks:"]
    for result in results:
        lines.append(f"- [{result.status.value}] {result.message}")
    return "\n".join(lines)


def render_migration_plan(plan: MigrationPlan) -> str:
    """Render a recommended migration plan for CLI output."""
    lines = [f"{step.step_number}. {step.title}" for step in plan.steps]
    return _render_section("Migration Plan", lines)


def render_rollback_notes(notes: list[str]) -> str:
    """Render rollback guidance for CLI output."""
    lines = [f"- {note}" for note in notes] if notes else []
    return _render_section("Rollback Notes", lines)


def render_audit_log(audit_log_path: str) -> str:
    """Render the saved audit log path for CLI output."""
    return _render_section("Audit Log", [audit_log_path])


def render_review_result(result: ReviewResult) -> str:
    """Render a structured change review result for CLI output."""
    if result.check_results:
        check_lines = [
            f"- [{check.status.value}] ({check.source}) {check.message}"
            for check in result.check_results
        ]
    else:
        check_lines = []

    if result.impacted_assets:
        impacted_lines = [f"- {asset}" for asset in result.impacted_assets]
    else:
        impacted_lines = []

    if result.reasons:
        reason_lines = [f"- {reason}" for reason in result.reasons]
    else:
        reason_lines = []

    sections = [
        _render_section("Decision", [result.decision.value]),
        _render_section("Risk Level", [result.risk_level.value]),
        _render_section("Checks", check_lines),
        _render_section("Impacted Assets", impacted_lines),
        _render_section("Reasons", reason_lines),
    ]

    if result.migration_plan and result.migration_plan.steps:
        sections.append(render_migration_plan(result.migration_plan))

    if result.rollback_notes:
        sections.append(render_rollback_notes(result.rollback_notes))

    return "\n\n".join(sections)


def render_propose_output(
    request: ChangeRequest,
    review: ReviewResult,
    audit_log_path: str | None = None,
) -> str:
    """Render a proposed change with its full review result."""
    sections = [render_change_request(request), render_review_result(review)]
    if audit_log_path is not None:
        sections.append(render_audit_log(audit_log_path))
    return "\n\n".join(sections)
