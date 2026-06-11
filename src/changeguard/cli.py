"""ChangeGuard CLI entry point."""

from pathlib import Path

import typer

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


if __name__ == "__main__":
    app()
