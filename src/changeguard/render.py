"""CLI-friendly review result rendering."""

from changeguard.models import ChangeRequest, TableMetadata


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
