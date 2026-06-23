"""Tests for migration plan models."""

from changeguard.models import MigrationPlan, MigrationStep


def test_migration_step_model() -> None:
    step = MigrationStep(
        step_number=1,
        title="Add new column as nullable",
        description="Add order_amount as a nullable column alongside amount.",
        required=True,
        validation_hint="Confirm column exists in target table schema.",
    )

    assert step.step_number == 1
    assert step.required is True
    assert step.validation_hint == "Confirm column exists in target table schema."


def test_migration_step_allows_optional_validation_hint() -> None:
    step = MigrationStep(
        step_number=2,
        title="Backfill new column from old column",
        description="Copy values from amount into order_amount.",
        required=True,
    )

    assert step.validation_hint is None


def test_migration_plan_model() -> None:
    plan = MigrationPlan(
        steps=[
            MigrationStep(
                step_number=1,
                title="Add new column as nullable",
                description="Add order_amount as a nullable column alongside amount.",
                required=True,
            ),
            MigrationStep(
                step_number=2,
                title="Backfill new column from old column",
                description="Copy values from amount into order_amount.",
                required=True,
                validation_hint="Row counts should match before and after backfill.",
            ),
        ]
    )

    assert len(plan.steps) == 2
    assert plan.steps[0].title == "Add new column as nullable"
    assert plan.steps[1].step_number == 2


def test_migration_plan_serialization_round_trip() -> None:
    plan = MigrationPlan(
        steps=[
            MigrationStep(
                step_number=1,
                title="Deprecate old column",
                description="Stop writing to amount after downstream migration.",
                required=False,
            )
        ]
    )

    payload = plan.model_dump(mode="json")
    restored = MigrationPlan.model_validate(payload)

    assert restored == plan
