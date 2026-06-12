"""CLI-friendly review result rendering."""

from changeguard.models import TableMetadata


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
