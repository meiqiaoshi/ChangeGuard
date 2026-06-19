"""Tests for column-level lineage impact lookup."""

from pathlib import Path

import pytest

from changeguard.lineage import find_column_impact, load_lineage, parse_column_reference

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "lineage"


@pytest.fixture
def sample_graph():
    return load_lineage(EXAMPLES_DIR / "sample_lineage.yml")


def test_parse_column_reference() -> None:
    assert parse_column_reference("sales.amount") == ("sales", "amount")


def test_parse_column_reference_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="Invalid column reference"):
        parse_column_reference("sales")


def test_find_column_impact_for_sales_amount(sample_graph) -> None:
    impacts = find_column_impact(sample_graph, "sales.amount")

    asset_names = {impact.asset.name for impact in impacts}
    assert "mart_daily_revenue" in asset_names
    assert "sales_dashboard" in asset_names

    impact_by_asset = {impact.asset.name: impact for impact in impacts}
    assert impact_by_asset["mart_daily_revenue"].target_column == "total_amount"
    assert impact_by_asset["sales_dashboard"].target_column == "revenue_kpi"


def test_find_column_impact_for_sales_customer_id(sample_graph) -> None:
    impacts = find_column_impact(sample_graph, "sales.customer_id")

    assert len(impacts) == 1
    assert impacts[0].asset.name == "customer_orders_summary"
    assert impacts[0].target_column == "customer_id"


def test_find_column_impact_returns_empty_for_unknown_column(sample_graph) -> None:
    impacts = find_column_impact(sample_graph, "sales.legacy_flag")

    assert impacts == []
