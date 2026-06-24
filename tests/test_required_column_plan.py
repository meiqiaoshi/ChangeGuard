"""Tests for required column migration plan generation."""

from changeguard.models import ChangeRequest, ChangeType
from changeguard.planner import generate_required_column_migration_plan


def test_generate_required_column_migration_plan_recommends_backfill_and_default() -> None:
    request = ChangeRequest(
        change_type=ChangeType.ADD_COLUMN,
        table="sales",
        column="region_code",
        column_type="string",
        nullable=False,
    )

    plan = generate_required_column_migration_plan(request)

    assert plan is not None
    assert len(plan.steps) == 4
    assert [step.step_number for step in plan.steps] == [1, 2, 3, 4]
    assert plan.steps[0].title == "Add column as nullable or provide default"
    assert "nullable" in plan.steps[0].description.lower()
    assert "default" in plan.steps[0].description.lower()
    assert plan.steps[1].title == "Backfill existing records"
    assert "region_code" in plan.steps[1].description
    assert plan.steps[2].title == "Validate non-null coverage"
    assert plan.steps[3].title == "Tighten contract after validation"
    assert "required" in plan.steps[3].description.lower()


def test_generate_required_column_migration_plan_returns_none_for_nullable_add() -> None:
    request = ChangeRequest(
        change_type=ChangeType.ADD_COLUMN,
        table="sales",
        column="discount",
        column_type="float",
        nullable=True,
    )

    assert generate_required_column_migration_plan(request) is None


def test_generate_required_column_migration_plan_returns_none_for_other_change_types() -> None:
    request = ChangeRequest(
        change_type=ChangeType.DROP_COLUMN,
        table="sales",
        column="status",
    )

    assert generate_required_column_migration_plan(request) is None
