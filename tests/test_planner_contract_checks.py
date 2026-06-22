"""Tests for contract checks in the review planner."""

from pathlib import Path

from changeguard.changes import load_change_request, validate_rename_column
from changeguard.models import ChangeRequest, ChangeType, Decision, RiskLevel
from changeguard.planner import review_change
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_review_change_blocks_rename_of_required_contract_column(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
    )

    request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )
    result = review_change(project, request)

    assert result.decision == Decision.BLOCK
    assert result.risk_level == RiskLevel.HIGH
    assert any("required by contract" in reason for reason in result.reasons)
    assert any(check.source == "contract" for check in result.check_results)


def test_review_change_allows_nullable_add_column_with_contract(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
    )

    request = ChangeRequest(
        change_type=ChangeType.ADD_COLUMN,
        table="sales",
        column="discount",
        column_type="float",
        nullable=True,
    )
    result = review_change(project, request)

    assert result.decision == Decision.ALLOW
    assert result.risk_level == RiskLevel.LOW
    assert any(check.name == "contract_add_nullable_column" for check in result.check_results)
