"""Lineage metadata loading and impact lookup."""

from pathlib import Path

import yaml

from changeguard.models import AssetRef, AssetType, LineageEdge, LineageGraph


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
