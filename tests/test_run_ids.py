"""Tests for sequential review run ID generation."""

import json
from pathlib import Path

from changeguard.audit import next_run_id
from changeguard.workspace import init_workspace, runs_path


def test_next_run_id_starts_at_one_for_empty_workspace(tmp_path: Path) -> None:
    init_workspace(tmp_path)

    assert next_run_id(tmp_path) == "000001"


def test_next_run_id_increments_sequentially(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    runs_dir = runs_path(tmp_path)

    (runs_dir / "000001.json").write_text(json.dumps({"run_id": "000001"}) + "\n", encoding="utf-8")
    assert next_run_id(tmp_path) == "000002"

    (runs_dir / "000002.json").write_text(json.dumps({"run_id": "000002"}) + "\n", encoding="utf-8")
    assert next_run_id(tmp_path) == "000003"


def test_next_run_id_uses_highest_existing_id(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    runs_dir = runs_path(tmp_path)

    (runs_dir / "000005.json").write_text(json.dumps({"run_id": "000005"}) + "\n", encoding="utf-8")

    assert next_run_id(tmp_path) == "000006"
