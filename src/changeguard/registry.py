"""Table registry load, save, and registration."""

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from changeguard.models import TableMetadata
from changeguard.workspace import registry_path


class DuplicateTableError(ValueError):
    """Raised when registering a table name that already exists."""


class Registry(BaseModel):
    """Collection of registered table metadata."""

    tables: list[TableMetadata] = Field(default_factory=list)


def load_registry(base: Path | None = None) -> Registry:
    """Load the table registry from the workspace JSON file."""
    path = registry_path(base)
    if not path.exists():
        return Registry()

    data = json.loads(path.read_text(encoding="utf-8"))
    return Registry.model_validate(data)


def save_registry(base: Path | None, registry: Registry) -> None:
    """Persist the table registry to the workspace JSON file."""
    path = registry_path(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(registry.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )


def _resolve_path(base: Path, path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate


def _store_path(base: Path, path: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def register_table(
    base: Path | None,
    name: str,
    schema_path: str | Path,
    contract_path: str | Path | None = None,
    lineage_path: str | Path | None = None,
    owner: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> tuple[TableMetadata, list[str]]:
    """Register a table in the workspace registry."""
    project_base = base or Path.cwd()
    warnings: list[str] = []

    schema = _resolve_path(project_base, schema_path)
    if not schema.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    if contract_path is None:
        warnings.append("No contract path provided.")
        stored_contract_path = ""
    else:
        contract = _resolve_path(project_base, contract_path)
        if not contract.exists():
            warnings.append(f"Contract file not found: {contract_path}")
        stored_contract_path = _store_path(project_base, contract)

    stored_lineage_path: str | None = None
    if lineage_path is not None:
        lineage = _resolve_path(project_base, lineage_path)
        if not lineage.exists():
            warnings.append(f"Lineage file not found: {lineage_path}")
        stored_lineage_path = _store_path(project_base, lineage)

    registry = load_registry(project_base)
    if any(table.name == name for table in registry.tables):
        raise DuplicateTableError(f"Table already registered: {name}")

    now = datetime.now(timezone.utc)
    table = TableMetadata(
        name=name,
        schema_path=_store_path(project_base, schema),
        contract_path=stored_contract_path,
        lineage_path=stored_lineage_path,
        owner=owner,
        description=description,
        tags=tags or [],
        created_at=now,
        updated_at=now,
    )
    registry.tables.append(table)
    save_registry(project_base, registry)
    return table, warnings
