"""Tests for lineage checks in the review planner."""

from pathlib import Path

from changeguard.changes import load_change_request, validate_rename_column
from changeguard.models import CheckStatus, Decision, RiskLevel
from changeguard.planner import review_change
from changeguard.registry import register_table
from changeguard.workspace import init_workspace

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_review_change_blocks_rename_due_to_lineage(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        lineage_path=str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
    )

    request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )
    result = review_change(project, request)

    assert result.decision == Decision.BLOCK
    assert result.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
    lineage_checks = [check for check in result.check_results if check.source == "lineage"]
    assert len(lineage_checks) == 1
    assert lineage_checks[0].status == CheckStatus.FAIL
    assert "mart_daily_revenue" in lineage_checks[0].message
    assert "mart_daily_revenue.total_amount" in result.impacted_assets
