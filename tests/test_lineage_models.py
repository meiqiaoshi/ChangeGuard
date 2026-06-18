"""Tests for lineage metadata models."""

from changeguard.models import AssetRef, AssetType, LineageEdge, LineageGraph


def test_asset_ref_supports_table_and_column() -> None:
    table_ref = AssetRef(name="sales", asset_type=AssetType.TABLE)
    column_ref = AssetRef(
        name="sales.amount",
        asset_type=AssetType.COLUMN,
        column="amount",
    )

    assert table_ref.asset_type == AssetType.TABLE
    assert column_ref.column == "amount"


def test_asset_ref_accepts_type_alias() -> None:
    ref = AssetRef.model_validate({"name": "sales_dashboard", "type": "dashboard"})

    assert ref.asset_type == AssetType.DASHBOARD


def test_lineage_edge_links_source_and_target() -> None:
    edge = LineageEdge(
        source=AssetRef(name="sales", asset_type=AssetType.TABLE),
        target=AssetRef(name="mart_daily_revenue", asset_type=AssetType.MART),
        source_column="amount",
        target_column="total_amount",
    )

    assert edge.source.name == "sales"
    assert edge.target.name == "mart_daily_revenue"
    assert edge.source_column == "amount"
    assert edge.target_column == "total_amount"


def test_lineage_graph_stores_assets_and_edges() -> None:
    sales = AssetRef(name="sales", asset_type=AssetType.TABLE)
    dashboard = AssetRef(name="sales_dashboard", asset_type=AssetType.DASHBOARD)
    edge = LineageEdge(
        source=sales,
        target=dashboard,
        source_column="amount",
        target_column="revenue_kpi",
    )

    graph = LineageGraph(version="1.0", assets=[sales, dashboard], edges=[edge])

    assert graph.version == "1.0"
    assert len(graph.assets) == 2
    assert len(graph.edges) == 1
    assert graph.edges[0].target.asset_type == AssetType.DASHBOARD


def test_lineage_graph_serialization_round_trip() -> None:
    graph = LineageGraph(
        edges=[
            LineageEdge(
                source=AssetRef(name="sales", asset_type=AssetType.TABLE),
                target=AssetRef(name="customer_orders_summary", asset_type=AssetType.MART),
                source_column="customer_id",
                target_column="customer_id",
            )
        ]
    )

    payload = graph.model_dump(mode="json")
    restored = LineageGraph.model_validate(payload)

    assert restored == graph
