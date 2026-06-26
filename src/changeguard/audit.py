"""Review run persistence and audit log management."""

import json
from pathlib import Path

from changeguard.models import ReviewResult
from changeguard.workspace import runs_path

RUN_ID_WIDTH = 6


class ReviewRunNotFoundError(LookupError):
    """Raised when a saved review run cannot be found."""


def next_run_id(base: Path | None = None) -> str:
    """Return the next sequential review run ID for the workspace."""
    runs_dir = runs_path(base)
    runs_dir.mkdir(parents=True, exist_ok=True)

    highest = 0
    for path in runs_dir.glob("*.json"):
        if path.stem.isdigit():
            highest = max(highest, int(path.stem))

    return str(highest + 1).zfill(RUN_ID_WIDTH)


def save_review_run(base: Path | None, review_result: ReviewResult) -> Path:
    """Persist a review result as a JSON audit log in the workspace runs directory."""
    run_id = next_run_id(base)
    run_file = runs_path(base) / f"{run_id}.json"
    run_file.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "run_id": run_id,
        **review_result.model_dump(mode="json"),
    }
    run_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return run_file


def format_audit_log_path(run_file: Path, base: Path | None = None) -> str:
    """Format a saved audit log path for CLI output."""
    project_base = base or Path.cwd()
    try:
        return str(run_file.relative_to(project_base))
    except ValueError:
        return str(run_file)


def _normalize_run_id(run_id: str) -> str:
    if run_id.isdigit():
        return str(int(run_id)).zfill(RUN_ID_WIDTH)
    return run_id


def list_runs(base: Path | None = None) -> list[str]:
    """List saved review run IDs in ascending order."""
    runs_dir = runs_path(base)
    if not runs_dir.exists():
        return []

    run_ids = [path.stem for path in runs_dir.glob("*.json") if path.stem.isdigit()]
    return sorted(run_ids)


def load_run(base: Path | None, run_id: str) -> ReviewResult:
    """Load a saved review result from the workspace runs directory."""
    normalized_run_id = _normalize_run_id(run_id)
    run_file = runs_path(base) / f"{normalized_run_id}.json"
    if not run_file.is_file():
        raise ReviewRunNotFoundError(f"Review run not found: {run_id}")

    payload = json.loads(run_file.read_text(encoding="utf-8"))
    payload.pop("run_id", None)
    return ReviewResult.model_validate(payload)
