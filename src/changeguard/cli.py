"""ChangeGuard CLI entry point."""

from pathlib import Path

import typer

from changeguard.registry import (
    DuplicateTableError,
    TableNotFoundError,
    get_table,
    load_registry,
    register_table,
)
from changeguard.render import render_table_inspection, render_table_list
from changeguard.workspace import WORKSPACE_DIR_NAME, init_workspace

app = typer.Typer(
    name="changeguard",
    help="A local-first data platform change safety checker.",
    no_args_is_help=True,
    invoke_without_command=True,
)


@app.callback()
def main() -> None:
    """ChangeGuard CLI root command."""
    pass


@app.command("init")
def init_cmd(
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """Initialize a local ChangeGuard workspace."""
    init_workspace(path or Path.cwd())
    typer.echo(f"Initialized ChangeGuard workspace at {WORKSPACE_DIR_NAME}")


@app.command("register-table")
def register_table_cmd(
    name: str = typer.Option(..., "--name", help="Registered table name."),
    schema: Path = typer.Option(..., "--schema", help="Path to the schema file."),
    contract: Path | None = typer.Option(
        None,
        "--contract",
        help="Path to the contract file.",
    ),
    lineage: Path | None = typer.Option(
        None,
        "--lineage",
        help="Path to the lineage file.",
    ),
    owner: str | None = typer.Option(None, "--owner", help="Table owner."),
    description: str | None = typer.Option(None, "--description", help="Table description."),
    tag: list[str] | None = typer.Option(None, "--tag", help="Table tag. Repeatable."),
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """Register a table in the local ChangeGuard workspace."""
    base = path or Path.cwd()
    try:
        table, warnings = register_table(
            base,
            name=name,
            schema_path=schema,
            contract_path=contract,
            lineage_path=lineage,
            owner=owner,
            description=description,
            tags=tag,
        )
    except FileNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    except DuplicateTableError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Registered table: {table.name}")
    for warning in warnings:
        typer.echo(f"Warning: {warning}")


@app.command("tables")
def tables_cmd(
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """List registered tables."""
    registry = load_registry(path or Path.cwd())
    typer.echo(render_table_list(registry.tables))


@app.command("inspect")
def inspect_cmd(
    name: str = typer.Argument(..., help="Registered table name."),
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """Show metadata for a registered table."""
    try:
        table = get_table(path or Path.cwd(), name)
    except TableNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(render_table_inspection(table))


if __name__ == "__main__":
    app()
