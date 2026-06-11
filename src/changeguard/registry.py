"""Table registry load, save, and registration."""

import json
from pathlib import Path

from pydantic import BaseModel, Field

from changeguard.models import TableMetadata
from changeguard.workspace import registry_path


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
