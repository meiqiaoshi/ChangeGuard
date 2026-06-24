"""Tests for rename column migration plan generation."""

from pathlib import Path

from changeguard.changes import load_change_request, validate_rename_column
from changeguard.models import ChangeRequest, ChangeType
from changeguard.planner import generate_rename_column_migration_plan

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_generate_rename_column_migration_plan_includes_compatibility_strategy() -> None:
    request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )

    plan = generate_rename_column_migration_plan(
        request,
        impacted_assets=[
            "mart_daily_revenue.total_amount",
            "sales_dashboard.revenue_kpi",
        ],
    )

    assert plan is not None
    assert len(plan.steps) == 6
    assert [step.step_number for step in plan.steps] == [1, 2, 3, 4, 5, 6]
    assert plan.steps[0].title == "Add new column as nullable"
    assert "order_amount" in plan.steps[0].description
    assert plan.steps[1].title == "Backfill new column from old column"
    assert "amount" in plan.steps[1].description
    assert plan.steps[2].title == "Update downstream assets"
    assert "mart_daily_revenue.total_amount" in plan.steps[2].description
    assert plan.steps[3].title == "Run contract checks"
    assert plan.steps[4].title == "Run quality checks"
    assert plan.steps[5].title == "Deprecate old column after compatibility window"
    assert plan.steps[5].required is False


def test_generate_rename_column_migration_plan_returns_none_for_other_change_types() -> None:
    request = ChangeRequest(
        change_type=ChangeType.DROP_COLUMN,
        table="sales",
        column="status",
    )

    assert generate_rename_column_migration_plan(request) is None
