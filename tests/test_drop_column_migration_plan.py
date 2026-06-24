"""Tests for drop column migration plan generation."""

from pathlib import Path

from changeguard.changes import load_change_request, validate_drop_column
from changeguard.models import ChangeRequest, ChangeType
from changeguard.planner import generate_drop_column_migration_plan

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_generate_drop_column_migration_plan_includes_deprecation_window() -> None:
    request = validate_drop_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "drop_customer_id.yml")
    )

    plan = generate_drop_column_migration_plan(
        request,
        impacted_assets=["customer_orders_summary.customer_id"],
    )

    assert plan is not None
    assert len(plan.steps) == 5
    assert [step.step_number for step in plan.steps] == [1, 2, 3, 4, 5]
    assert plan.steps[0].title == "Check downstream usage"
    assert "customer_id" in plan.steps[0].description
    assert "customer_orders_summary.customer_id" in plan.steps[0].description
    assert plan.steps[1].title == "Mark column deprecated"
    assert "deprecated" in plan.steps[1].description.lower()
    assert plan.steps[2].title == "Update consumers"
    assert plan.steps[3].title == "Run validation"
    assert plan.steps[4].title == "Remove after compatibility window"
    assert "compatibility window" in plan.steps[4].description.lower()
    assert plan.steps[4].required is False


def test_generate_drop_column_migration_plan_returns_none_for_other_change_types() -> None:
    request = ChangeRequest(
        change_type=ChangeType.RENAME_COLUMN,
        table="sales",
        column="amount",
        new_name="order_amount",
    )

    assert generate_drop_column_migration_plan(request) is None
