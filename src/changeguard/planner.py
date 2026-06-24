"""Review planner orchestrating the full change review pipeline."""

from pathlib import Path

from changeguard.contracts import check_change_against_contract, load_contract
from changeguard.lineage import find_column_impact, load_lineage
from changeguard.models import (
    ChangeRequest,
    ChangeType,
    CheckStatus,
    MigrationPlan,
    MigrationStep,
    ReviewResult,
)
from changeguard.registry import TableNotFoundError, get_table
from changeguard.rules import aggregate_decision, check_change_against_lineage, score_risk_level


def _load_contract_checks(base: Path, change_request: ChangeRequest):
    table = get_table(base, change_request.table)
    if not table.contract_path:
        return []

    contract_file = Path(table.contract_path)
    if not contract_file.is_absolute():
        contract_file = base / contract_file

    contract = load_contract(contract_file)
    return check_change_against_contract(contract, change_request)


def _load_lineage_checks(base: Path, change_request: ChangeRequest):
    table = get_table(base, change_request.table)
    if not table.lineage_path:
        return [], []

    lineage_file = Path(table.lineage_path)
    if not lineage_file.is_absolute():
        lineage_file = base / lineage_file

    graph = load_lineage(lineage_file)
    check_results = check_change_against_lineage(graph, change_request)

    impacted_assets: list[str] = []
    if (
        change_request.column
        and change_request.change_type in (ChangeType.RENAME_COLUMN, ChangeType.DROP_COLUMN)
    ):
        reference = f"{change_request.table}.{change_request.column}"
        impacted_assets = [
            (
                f"{impact.asset.name}.{impact.target_column}"
                if impact.target_column
                else impact.asset.name
            )
            for impact in find_column_impact(graph, reference)
        ]

    return check_results, impacted_assets


def generate_rename_column_migration_plan(
    change_request: ChangeRequest,
    impacted_assets: list[str] | None = None,
) -> MigrationPlan | None:
    """Generate a compatibility migration plan for an unsafe column rename."""
    if change_request.change_type != ChangeType.RENAME_COLUMN:
        return None
    if not change_request.column or not change_request.new_name:
        return None

    table = change_request.table
    old_column = change_request.column
    new_column = change_request.new_name
    downstream = impacted_assets or []
    downstream_summary = (
        ", ".join(downstream)
        if downstream
        else "all known downstream assets that reference the old column"
    )

    return MigrationPlan(
        steps=[
            MigrationStep(
                step_number=1,
                title="Add new column as nullable",
                description=(
                    f"Add {new_column} as a nullable column on {table} "
                    f"alongside {old_column}."
                ),
                required=True,
                validation_hint=(
                    f"Confirm {table}.{new_column} exists and remains nullable."
                ),
            ),
            MigrationStep(
                step_number=2,
                title="Backfill new column from old column",
                description=(
                    f"Copy values from {table}.{old_column} into {table}.{new_column} "
                    "for all existing rows."
                ),
                required=True,
                validation_hint="Row counts and sampled values should match after backfill.",
            ),
            MigrationStep(
                step_number=3,
                title="Update downstream assets",
                description=(
                    f"Update {downstream_summary} to read {new_column} "
                    f"instead of {old_column}."
                ),
                required=True,
                validation_hint="Downstream jobs and dashboards should pass smoke tests.",
            ),
            MigrationStep(
                step_number=4,
                title="Run contract checks",
                description=(
                    f"Validate {table}.{new_column} against the data contract "
                    "before removing the old column."
                ),
                required=True,
                validation_hint="Contract checks for the new column should pass.",
            ),
            MigrationStep(
                step_number=5,
                title="Run quality checks",
                description=(
                    f"Run data quality checks on {table}.{new_column} "
                    "and impacted downstream assets."
                ),
                required=True,
                validation_hint="Quality checks should show no regressions.",
            ),
            MigrationStep(
                step_number=6,
                title="Deprecate old column after compatibility window",
                description=(
                    f"Stop writing to {table}.{old_column}, monitor through a "
                    "compatibility window, then remove the old column."
                ),
                required=False,
                validation_hint=(
                    "No consumers should reference the old column before drop."
                ),
            ),
        ]
    )


def generate_drop_column_migration_plan(
    change_request: ChangeRequest,
    impacted_assets: list[str] | None = None,
) -> MigrationPlan | None:
    """Generate a deprecation migration plan for an unsafe column drop."""
    if change_request.change_type != ChangeType.DROP_COLUMN:
        return None
    if not change_request.column:
        return None

    table = change_request.table
    column = change_request.column
    downstream = impacted_assets or []
    downstream_summary = (
        ", ".join(downstream)
        if downstream
        else "all known downstream assets that reference the column"
    )

    return MigrationPlan(
        steps=[
            MigrationStep(
                step_number=1,
                title="Check downstream usage",
                description=(
                    f"Confirm which assets depend on {table}.{column}, "
                    f"including {downstream_summary}."
                ),
                required=True,
                validation_hint="Document all downstream references before deprecation.",
            ),
            MigrationStep(
                step_number=2,
                title="Mark column deprecated",
                description=(
                    f"Mark {table}.{column} as deprecated in schema metadata "
                    "and communicate the planned removal date."
                ),
                required=True,
                validation_hint="Deprecation should be visible to data producers and consumers.",
            ),
            MigrationStep(
                step_number=3,
                title="Update consumers",
                description=(
                    f"Update {downstream_summary} to stop depending on {table}.{column}."
                ),
                required=True,
                validation_hint="Consumers should pass smoke tests without the column.",
            ),
            MigrationStep(
                step_number=4,
                title="Run validation",
                description=(
                    f"Run contract and quality validation for {table} "
                    "and impacted downstream assets."
                ),
                required=True,
                validation_hint="Validation should confirm no remaining dependency on the column.",
            ),
            MigrationStep(
                step_number=5,
                title="Remove after compatibility window",
                description=(
                    f"Drop {table}.{column} only after a compatibility window "
                    "with no active downstream usage."
                ),
                required=False,
                validation_hint=(
                    "No jobs, dashboards, or contracts should reference the column."
                ),
            ),
        ]
    )


def generate_required_column_migration_plan(
    change_request: ChangeRequest,
) -> MigrationPlan | None:
    """Generate a backfill migration plan for adding a required column."""
    if change_request.change_type != ChangeType.ADD_COLUMN:
        return None
    if not change_request.column or change_request.nullable is not False:
        return None

    table = change_request.table
    column = change_request.column
    column_type = change_request.column_type or "the target type"

    return MigrationPlan(
        steps=[
            MigrationStep(
                step_number=1,
                title="Add column as nullable or provide default",
                description=(
                    f"Add {table}.{column} as nullable or with a safe default "
                    f"({column_type}) so existing rows remain valid."
                ),
                required=True,
                validation_hint=(
                    "Choose nullable rollout or a default that satisfies downstream needs."
                ),
            ),
            MigrationStep(
                step_number=2,
                title="Backfill existing records",
                description=(
                    f"Populate {table}.{column} for all existing rows before "
                    "making the column required."
                ),
                required=True,
                validation_hint="Backfill logic should cover historical partitions.",
            ),
            MigrationStep(
                step_number=3,
                title="Validate non-null coverage",
                description=(
                    f"Confirm {table}.{column} has no null values across "
                    "existing and newly ingested data."
                ),
                required=True,
                validation_hint="Null-rate checks should reach zero before tightening.",
            ),
            MigrationStep(
                step_number=4,
                title="Tighten contract after validation",
                description=(
                    f"Update schema and contract metadata to mark {table}.{column} "
                    "as required only after backfill validation succeeds."
                ),
                required=True,
                validation_hint="Contract and schema should match enforced nullability.",
            ),
        ]
    )


def generate_migration_plan(
    change_request: ChangeRequest,
    impacted_assets: list[str] | None = None,
) -> MigrationPlan | None:
    """Generate a migration plan for supported change request types."""
    if change_request.change_type == ChangeType.RENAME_COLUMN:
        return generate_rename_column_migration_plan(change_request, impacted_assets)
    if change_request.change_type == ChangeType.DROP_COLUMN:
        return generate_drop_column_migration_plan(change_request, impacted_assets)
    if change_request.change_type == ChangeType.ADD_COLUMN:
        return generate_required_column_migration_plan(change_request)
    return None


def review_change(base: Path | None, change_request: ChangeRequest) -> ReviewResult:
    """Review a proposed change and return a structured review result.

    Runs contract and lineage checks when the table is registered in the workspace.
    Used by the ``propose`` CLI command.
    """
    project_base = base or Path.cwd()
    check_results = []
    impacted_assets: list[str] = []

    try:
        check_results.extend(_load_contract_checks(project_base, change_request))
    except (TableNotFoundError, FileNotFoundError, ValueError):
        pass

    try:
        lineage_checks, lineage_impacts = _load_lineage_checks(project_base, change_request)
        check_results.extend(lineage_checks)
        impacted_assets.extend(lineage_impacts)
    except (TableNotFoundError, FileNotFoundError, ValueError):
        pass

    decision = aggregate_decision(check_results)
    risk_level = score_risk_level(decision, check_results, change_request)
    reasons = [
        result.message
        for result in check_results
        if result.status in (CheckStatus.WARN, CheckStatus.FAIL)
    ]
    migration_plan = generate_migration_plan(change_request, impacted_assets)

    return ReviewResult(
        decision=decision,
        risk_level=risk_level,
        reasons=reasons,
        check_results=check_results,
        impacted_assets=impacted_assets,
        migration_plan=migration_plan,
    )
