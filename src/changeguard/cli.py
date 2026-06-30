"""ChangeGuard CLI entry point."""

from pathlib import Path

import typer
from pydantic import ValidationError

from changeguard.audit import (
    ReviewRunNotFoundError,
    format_audit_log_path,
    list_run_summaries,
    load_run,
    save_review_run,
)
from changeguard.changes import (
    ChangeValidationError,
    build_change_request,
    load_change_request,
)
from changeguard.contracts import load_contract
from changeguard.explain import explain_review
from changeguard.lineage import find_column_impact, find_downstream, load_lineage
from changeguard.models import AssetRef, AssetType, ChangeType
from changeguard.planner import review_change
from changeguard.registry import (
    DuplicateTableError,
    TableNotFoundError,
    get_table,
    load_registry,
    register_table,
)
from changeguard.render import (
    render_column_impact_list,
    render_contract_summary,
    render_downstream_impact_list,
    render_propose_output,
    render_review_result,
    render_runs_list,
    render_table_inspection,
    render_table_list,
)
from changeguard.workspace import WORKSPACE_DIR_NAME, init_workspace


def _parse_nullable(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ChangeValidationError(f"Invalid nullable value: {value}")


app = typer.Typer(
    name="changeguard",
    help="A local-first data platform change safety checker.",
    no_args_is_help=True,
    invoke_without_command=True,
)


def _load_lineage_for_table(base: Path, table_name: str):
    table = get_table(base, table_name)
    if not table.lineage_path:
        raise ValueError(f"No lineage path registered for table: {table_name}")

    lineage_file = Path(table.lineage_path)
    if not lineage_file.is_absolute():
        lineage_file = base / lineage_file

    return load_lineage(lineage_file)


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


@app.command("check-contract")
def check_contract_cmd(
    name: str = typer.Argument(..., help="Registered table name."),
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """Load and summarize the contract for a registered table."""
    base = path or Path.cwd()
    try:
        table = get_table(base, name)
    except TableNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    if not table.contract_path:
        typer.secho(
            f"No contract path registered for table: {name}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    contract_file = Path(table.contract_path)
    if not contract_file.is_absolute():
        contract_file = base / contract_file

    try:
        contract = load_contract(contract_file)
    except FileNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(render_contract_summary(contract))


@app.command("impact")
def impact_cmd(
    reference: str = typer.Argument(
        ...,
        help="Table name or table.column reference.",
    ),
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """Show downstream assets impacted by a table or column."""
    base = path or Path.cwd()
    table_name = reference.split(".", 1)[0]

    try:
        graph = _load_lineage_for_table(base, table_name)
    except TableNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    except (ValueError, FileNotFoundError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    if "." in reference:
        typer.echo(render_column_impact_list(reference, find_column_impact(graph, reference)))
        return

    asset_ref = AssetRef(name=table_name, asset_type=AssetType.TABLE)
    typer.echo(render_downstream_impact_list(reference, find_downstream(graph, asset_ref)))


@app.command("propose")
def propose_cmd(
    file: Path | None = typer.Option(
        None,
        "--file",
        help="Path to a YAML change request file.",
    ),
    change_type: ChangeType | None = typer.Option(
        None,
        "--change-type",
        help="Change request type.",
    ),
    table: str | None = typer.Option(None, "--table", help="Target table name."),
    column: str | None = typer.Option(None, "--column", help="Target column name."),
    new_name: str | None = typer.Option(
        None,
        "--new-name",
        help="New column name for rename_column.",
    ),
    column_type: str | None = typer.Option(
        None,
        "--type",
        help="Column type for add_column.",
    ),
    new_type: str | None = typer.Option(
        None,
        "--new-type",
        help="New column type for change_column_type.",
    ),
    nullable: str | None = typer.Option(
        None,
        "--nullable",
        help="Nullability flag for add_column or set_nullable (true/false).",
    ),
    description: str | None = typer.Option(None, "--description", help="Change description."),
) -> None:
    """Load and review a proposed change from a YAML file or CLI flags."""
    try:
        if file is not None:
            request = load_change_request(file)
        elif change_type is not None:
            if not table:
                raise ChangeValidationError("table is required when using CLI flags")
            request = build_change_request(
                change_type=change_type,
                table=table,
                column=column,
                new_name=new_name,
                column_type=column_type,
                new_type=new_type,
                nullable=_parse_nullable(nullable),
                description=description,
            )
        else:
            typer.secho(
                "Provide --file or --change-type with change flags.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
    except FileNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    except (ChangeValidationError, ValidationError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    review = review_change(Path.cwd(), request)
    run_file = save_review_run(Path.cwd(), review, change_request=request)
    audit_reference = format_audit_log_path(run_file, Path.cwd())
    typer.echo(render_propose_output(request, review, audit_log_path=audit_reference))


@app.command("runs")
def runs_cmd(
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """List saved review runs in the workspace."""
    typer.echo(render_runs_list(list_run_summaries(path or Path.cwd())))


@app.command("review-run")
def review_run_cmd(
    run_id: str = typer.Argument(..., help="Saved review run ID."),
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """Render a saved review run from the audit log."""
    base = path or Path.cwd()
    try:
        review = load_run(base, run_id)
    except ReviewRunNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(render_review_result(review))


@app.command("explain-run")
def explain_run_cmd(
    run_id: str = typer.Argument(..., help="Saved review run ID."),
    path: Path | None = typer.Option(
        None,
        "--path",
        help="Base directory for the ChangeGuard workspace.",
    ),
) -> None:
    """Explain a saved review run in plain language."""
    base = path or Path.cwd()
    try:
        review = load_run(base, run_id)
    except ReviewRunNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(explain_review(review))


if __name__ == "__main__":
    app()
