"""Review run persistence and audit log management."""

from pathlib import Path

from changeguard.workspace import runs_path

RUN_ID_WIDTH = 6


def next_run_id(base: Path | None = None) -> str:
    """Return the next sequential review run ID for the workspace."""
    runs_dir = runs_path(base)
    runs_dir.mkdir(parents=True, exist_ok=True)

    highest = 0
    for path in runs_dir.glob("*.json"):
        if path.stem.isdigit():
            highest = max(highest, int(path.stem))

    return str(highest + 1).zfill(RUN_ID_WIDTH)
