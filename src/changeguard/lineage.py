"""Lineage metadata loading and impact lookup."""

from dataclasses import dataclass
from pathlib import Path

import yaml

from changeguard.models import AssetRef, AssetType, LineageEdge, LineageGraph


@dataclass(frozen=True)
class ColumnImpact:
    """Downstream asset impacted by a source column."""

    asset: AssetRef
    target_column: str | None = None


class LineageLoadError(ValueError):
    """Raised when a lineage file cannot be loaded."""


def _asset_type(value: str) -> AssetType:
    try:
        return AssetType(value)
    except ValueError:
        return AssetType.TABLE


def _asset_type_by_name(assets: list[AssetRef], name: str) -> AssetType:
    for asset in assets:
        if asset.name == name:
            return asset.asset_type
    return AssetType.TABLE


def load_lineage(path: Path) -> LineageGraph:
    """Load lineage metadata from a YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Lineage file not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise LineageLoadError("Lineage YAML must be a mapping")

    version = str(data.get("version", "1.0"))
    assets: list[AssetRef] = []
    edges: list[LineageEdge] = []

    for asset_data in data.get("assets", []):
        asset_ref = AssetRef(
            name=asset_data["name"],
            asset_type=_asset_type(asset_data.get("type", "table")),
        )
        assets.append(asset_ref)

        for dependency in asset_data.get("depends_on", []):
            source_table = dependency["table"]
            source_ref = AssetRef(name=source_table, asset_type=AssetType.TABLE)
            columns = dependency.get("columns", [])

            if columns:
                for column in columns:
                    edges.append(
                        LineageEdge(
                            source=source_ref,
                            target=asset_ref,
                            source_column=column,
                        )
                    )
            else:
                edges.append(LineageEdge(source=source_ref, target=asset_ref))

    for entry in data.get("column_lineage", []):
        source_table = entry["source_table"]
        source_column = entry["source_column"]
        source_ref = AssetRef(name=source_table, asset_type=AssetType.TABLE)

        for downstream in entry.get("downstream", []):
            target_name = downstream["asset"]
            target_ref = AssetRef(
                name=target_name,
                asset_type=_asset_type_by_name(assets, target_name),
            )
            edges.append(
                LineageEdge(
                    source=source_ref,
                    target=target_ref,
                    source_column=source_column,
                    target_column=downstream.get("column"),
                )
            )

    return LineageGraph(version=version, assets=assets, edges=edges)


def _get_asset_ref(graph: LineageGraph, name: str) -> AssetRef:
    for asset in graph.assets:
        if asset.name == name:
            return asset
    return AssetRef(name=name, asset_type=AssetType.TABLE)


def _direct_downstream(graph: LineageGraph, asset_ref: AssetRef) -> list[AssetRef]:
    downstream: list[AssetRef] = []
    seen: set[str] = set()

    for edge in graph.edges:
        if edge.source.name != asset_ref.name:
            continue
        if edge.target.name in seen:
            continue
        seen.add(edge.target.name)
        downstream.append(edge.target)

    return downstream


def find_downstream(
    graph: LineageGraph,
    asset_ref: AssetRef,
    depth: str | int = "all",
) -> list[AssetRef]:
    """Find downstream assets connected to the given asset."""
    direct = _direct_downstream(graph, asset_ref)
    if depth in ("direct", 1):
        return direct

    if depth not in ("all", -1):
        raise ValueError(f"Unsupported lineage depth: {depth}")

    downstream = list(direct)
    seen_names = {asset.name for asset in downstream}
    seen_names.add(asset_ref.name)
    queue = [asset.name for asset in direct]

    while queue:
        current_name = queue.pop(0)
        current_ref = _get_asset_ref(graph, current_name)

        for target in _direct_downstream(graph, current_ref):
            if target.name in seen_names:
                continue
            seen_names.add(target.name)
            downstream.append(target)
            queue.append(target.name)

    return downstream


def parse_column_reference(reference: str) -> tuple[str, str]:
    """Parse a column reference such as sales.amount."""
    parts = reference.split(".", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid column reference: {reference}")
    return parts[0], parts[1]


def find_column_impact(graph: LineageGraph, reference: str) -> list[ColumnImpact]:
    """Find downstream assets that depend on a source column."""
    table_name, column_name = parse_column_reference(reference)
    impacts_by_asset: dict[str, ColumnImpact] = {}

    for edge in graph.edges:
        if edge.source.name != table_name or edge.source_column != column_name:
            continue

        impact = ColumnImpact(asset=edge.target, target_column=edge.target_column)
        existing = impacts_by_asset.get(edge.target.name)
        if existing is None or (
            existing.target_column is None and impact.target_column is not None
        ):
            impacts_by_asset[edge.target.name] = impact

    return list(impacts_by_asset.values())
