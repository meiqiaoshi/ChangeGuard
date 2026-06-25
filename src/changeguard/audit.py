"""Review run persistence and audit log management."""

import json
from pathlib import Path

from changeguard.models import ReviewResult
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
