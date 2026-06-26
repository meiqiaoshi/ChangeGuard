"""Review run persistence and audit log management."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from changeguard.models import ChangeRequest, ReviewResult
from changeguard.workspace import runs_path

RUN_ID_WIDTH = 6


class ReviewRunNotFoundError(LookupError):
    """Raised when a saved review run cannot be found."""


@dataclass(frozen=True)
class ReviewRunSummary:
    """Summary metadata for a saved review run."""

    run_id: str
    decision: str
    risk_level: str
    change_type: str
    target: str
    created_at: str


def next_run_id(base: Path | None = None) -> str:
    """Return the next sequential review run ID for the workspace."""
    runs_dir = runs_path(base)
    runs_dir.mkdir(parents=True, exist_ok=True)

    highest = 0
    for path in runs_dir.glob("*.json"):
        if path.stem.isdigit():
            highest = max(highest, int(path.stem))

    return str(highest + 1).zfill(RUN_ID_WIDTH)


def _format_change_target(change_request: ChangeRequest) -> str:
    if change_request.column:
        return f"{change_request.table}.{change_request.column}"
    return change_request.table


def _strip_audit_metadata(payload: dict) -> dict:
    for key in ("run_id", "created_at", "change_type", "target"):
        payload.pop(key, None)
    return payload


def save_review_run(
    base: Path | None,
    review_result: ReviewResult,
    change_request: ChangeRequest | None = None,
    created_at: datetime | None = None,
) -> Path:
    """Persist a review result as a JSON audit log in the workspace runs directory."""
    run_id = next_run_id(base)
    run_file = runs_path(base) / f"{run_id}.json"
    run_file.parent.mkdir(parents=True, exist_ok=True)

    timestamp = created_at or datetime.now(timezone.utc)
    payload = {
        "run_id": run_id,
        "created_at": timestamp.isoformat(),
        **review_result.model_dump(mode="json"),
    }
    if change_request is not None:
        payload["change_type"] = change_request.change_type.value
        payload["target"] = _format_change_target(change_request)

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


def list_run_summaries(base: Path | None = None) -> list[ReviewRunSummary]:
    """Load summary metadata for all saved review runs."""
    summaries: list[ReviewRunSummary] = []
    for run_id in list_runs(base):
        run_file = runs_path(base) / f"{run_id}.json"
        payload = json.loads(run_file.read_text(encoding="utf-8"))
        summaries.append(
            ReviewRunSummary(
                run_id=payload.get("run_id", run_id),
                decision=payload["decision"],
                risk_level=payload["risk_level"],
                change_type=payload.get("change_type", "(unknown)"),
                target=payload.get("target", "(unknown)"),
                created_at=payload.get("created_at", "(unknown)"),
            )
        )
    return summaries


def load_run(base: Path | None, run_id: str) -> ReviewResult:
    """Load a saved review result from the workspace runs directory."""
    normalized_run_id = _normalize_run_id(run_id)
    run_file = runs_path(base) / f"{normalized_run_id}.json"
    if not run_file.is_file():
        raise ReviewRunNotFoundError(f"Review run not found: {run_id}")

    payload = json.loads(run_file.read_text(encoding="utf-8"))
    _strip_audit_metadata(payload)
    return ReviewResult.model_validate(payload)
