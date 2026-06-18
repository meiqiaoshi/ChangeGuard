"""Tests for loading lineage metadata from YAML."""

from pathlib import Path

import pytest

from changeguard.lineage import LineageLoadError, load_lineage
from changeguard.models import AssetType

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "lineage"


def test_load_sample_lineage_from_yaml() -> None:
    graph = load_lineage(EXAMPLES_DIR / "sample_lineage.yml")

    assert graph.version == "1.0"
    assert len(graph.assets) == 4
    assert graph.assets[0].name == "sales"
    assert graph.assets[0].asset_type == AssetType.TABLE
    assert any(asset.name == "sales_dashboard" for asset in graph.assets)
    assert len(graph.edges) > 0


def test_load_lineage_builds_column_level_edges() -> None:
    graph = load_lineage(EXAMPLES_DIR / "sample_lineage.yml")

    amount_edges = [
        edge
        for edge in graph.edges
        if edge.source.name == "sales"
        and edge.source_column == "amount"
    ]

    assert len(amount_edges) >= 2
    target_names = {edge.target.name for edge in amount_edges}
    assert "mart_daily_revenue" in target_names
    assert "sales_dashboard" in target_names


def test_load_lineage_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yml"

    with pytest.raises(FileNotFoundError, match="Lineage file not found"):
        load_lineage(missing)


def test_load_lineage_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yml"
    path.write_text("- not-a-mapping\n", encoding="utf-8")

    with pytest.raises(LineageLoadError, match="mapping"):
        load_lineage(path)
