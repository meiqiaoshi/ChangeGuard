"""Tests for downstream lineage lookup."""

from pathlib import Path

import pytest

from changeguard.lineage import find_downstream, load_lineage
from changeguard.models import AssetRef, AssetType

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "lineage"


@pytest.fixture
def sample_graph():
    return load_lineage(EXAMPLES_DIR / "sample_lineage.yml")


def test_find_direct_downstream_for_sales_table(sample_graph) -> None:
    sales = AssetRef(name="sales", asset_type=AssetType.TABLE)

    downstream = find_downstream(sample_graph, sales, depth="direct")
    names = {asset.name for asset in downstream}

    assert "mart_daily_revenue" in names
    assert "customer_orders_summary" in names
    assert "sales_dashboard" in names


def test_find_all_downstream_for_sales_table(sample_graph) -> None:
    sales = AssetRef(name="sales", asset_type=AssetType.TABLE)

    downstream = find_downstream(sample_graph, sales, depth="all")
    names = {asset.name for asset in downstream}

    assert "mart_daily_revenue" in names
    assert "customer_orders_summary" in names
    assert "sales_dashboard" in names


def test_find_all_downstream_includes_transitive_dependencies(sample_graph) -> None:
    mart = AssetRef(name="mart_daily_revenue", asset_type=AssetType.TABLE)

    downstream = find_downstream(sample_graph, mart, depth="all")

    assert len(downstream) == 1
    assert downstream[0].name == "sales_dashboard"


def test_find_downstream_returns_empty_for_leaf_asset(sample_graph) -> None:
    dashboard = AssetRef(name="sales_dashboard", asset_type=AssetType.DASHBOARD)

    downstream = find_downstream(sample_graph, dashboard, depth="all")

    assert downstream == []
