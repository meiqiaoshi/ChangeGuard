"""Shared Pydantic models for ChangeGuard."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TableMetadata(BaseModel):
    """Metadata for a table registered in the ChangeGuard workspace."""

    model_config = ConfigDict(extra="forbid")

    name: str
    schema_path: str
    contract_path: str
    lineage_path: str | None = None
    owner: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
