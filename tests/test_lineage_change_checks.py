"""Tests for lineage checks on rename and drop changes."""

from pathlib import Path

from changeguard.changes import validate_drop_column, validate_rename_column
from changeguard.lineage import (
    check_drop_column_against_lineage,
    check_rename_column_against_lineage,
    load_lineage,
)
from changeguard.models import ChangeRequest, ChangeType, CheckStatus
from changeguard.rules import check_change_against_lineage

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "lineage"


def _sample_graph():
    return load_lineage(EXAMPLES_DIR / "sample_lineage.yml")


def test_check_rename_column_blocks_when_column_has_downstream_users() -> None:
    graph = _sample_graph()
    request = validate_rename_column(
        ChangeRequest(
            change_type=ChangeType.RENAME_COLUMN,
            table="sales",
            column="amount",
            new_name="order_amount",
        )
    )

    results = check_rename_column_against_lineage(graph, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
    assert results[0].source == "lineage"
    assert "mart_daily_revenue" in results[0].message


def test_check_rename_column_warns_when_column_has_no_downstream_users() -> None:
    graph = _sample_graph()
    request = validate_rename_column(
        ChangeRequest(
            change_type=ChangeType.RENAME_COLUMN,
            table="sales",
            column="status",
            new_name="order_status",
        )
    )

    results = check_rename_column_against_lineage(graph, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN
    assert "no known downstream dependencies" in results[0].message


def test_check_drop_column_blocks_when_column_has_downstream_users() -> None:
    graph = _sample_graph()
    request = validate_drop_column(
        ChangeRequest(
            change_type=ChangeType.DROP_COLUMN,
            table="sales",
            column="customer_id",
        )
    )

    results = check_drop_column_against_lineage(graph, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
    assert "customer_orders_summary" in results[0].message


def test_check_drop_column_warns_when_column_has_no_downstream_users() -> None:
    graph = _sample_graph()
    request = validate_drop_column(
        ChangeRequest(
            change_type=ChangeType.DROP_COLUMN,
            table="sales",
            column="status",
        )
    )

    results = check_drop_column_against_lineage(graph, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.WARN


def test_check_change_against_lineage_dispatches_by_change_type() -> None:
    graph = _sample_graph()
    request = validate_drop_column(
        ChangeRequest(
            change_type=ChangeType.DROP_COLUMN,
            table="sales",
            column="amount",
        )
    )

    results = check_change_against_lineage(graph, request)

    assert len(results) == 1
    assert results[0].status == CheckStatus.FAIL
