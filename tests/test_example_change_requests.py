"""Tests for example change requests covering ALLOW, WARN, and BLOCK outcomes."""

from pathlib import Path

from changeguard.changes import load_change_request
from changeguard.models import Decision
from changeguard.planner import review_change
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "change_requests"


def _setup_sales(project: Path) -> None:
    examples = EXAMPLES_DIR.parent
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(examples / "schemas" / "sales_schema.json"),
        contract_path=str(examples / "contracts" / "sales_contract.yml"),
        lineage_path=str(examples / "lineage" / "sample_lineage.yml"),
    )


def test_allow_add_nullable_column_example(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    _setup_sales(project)

    request = load_change_request(EXAMPLES_DIR / "allow_add_nullable_column.yml")
    result = review_change(project, request)

    assert result.decision == Decision.ALLOW


def test_warn_drop_optional_column_example(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    _setup_sales(project)

    request = load_change_request(EXAMPLES_DIR / "warn_drop_optional_column.yml")
    result = review_change(project, request)

    assert result.decision == Decision.WARN


def test_block_rename_required_column_example(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    _setup_sales(project)

    request = load_change_request(EXAMPLES_DIR / "block_rename_required_column.yml")
    result = review_change(project, request)

    assert result.decision == Decision.BLOCK
