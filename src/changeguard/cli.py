"""ChangeGuard CLI entry point."""

import typer

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


if __name__ == "__main__":
    app()
