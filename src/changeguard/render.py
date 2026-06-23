"""CLI-friendly review result rendering."""

from changeguard.lineage import ColumnImpact
from changeguard.models import (
    AssetRef,
    ChangeRequest,
    CheckResult,
    CheckStatus,
    Contract,
    ReviewResult,
    TableMetadata,
)


def render_table_list(tables: list[TableMetadata]) -> str:
    """Render a list of registered table names."""
    if not tables:
        return "No tables registered."
    return "\n".join(table.name for table in tables)


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

    return "\n".join(lines)


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


def render_propose_output(request: ChangeRequest, review: ReviewResult) -> str:
    """Render a proposed change with its full review result."""
    return "\n".join([render_change_request(request), "", render_review_result(review)])


def render_review_result(result: ReviewResult) -> str:
    """Render a structured change review result for CLI output."""
    lines = [
        f"Decision: {result.decision.value}",
        f"Risk Level: {result.risk_level.value}",
        "",
        "Checks:",
    ]

    if result.check_results:
        for check in result.check_results:
            lines.append(f"- [{check.status.value}] ({check.source}) {check.message}")
    else:
        lines.append("- (none)")

    lines.extend(["", "Impacted Assets:"])
    if result.impacted_assets:
        for asset in result.impacted_assets:
            lines.append(f"- {asset}")
    else:
        lines.append("- (none)")

    lines.extend(["", "Reasons:"])
    if result.reasons:
        for reason in result.reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- (none)")

    return "\n".join(lines)
