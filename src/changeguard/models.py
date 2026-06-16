"""Shared Pydantic models for ChangeGuard."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ChangeType(str, Enum):
    """Supported change request types for the initial MVP."""

    ADD_COLUMN = "add_column"
    RENAME_COLUMN = "rename_column"
    DROP_COLUMN = "drop_column"
    CHANGE_COLUMN_TYPE = "change_column_type"
    SET_NULLABLE = "set_nullable"


class ChangeRequest(BaseModel):
    """Structured proposal for a single schema or contract change."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    change_type: ChangeType
    table: str
    column: str | None = None
    new_name: str | None = None
    column_type: str | None = Field(default=None, alias="type")
    new_type: str | None = None
    nullable: bool | None = None
    description: str | None = None
    requested_by: str | None = None


class ContractColumn(BaseModel):
    """Column expectations defined in a data contract."""

    model_config = ConfigDict(extra="forbid")

    type: str
    required: bool = False
    nullable: bool | None = None
    unique: bool = False
    primary_key: bool = False
    min_value: float | int | None = None
    max_value: float | int | None = None
    allowed_values: list[str] | None = None


class ContractRule(BaseModel):
    """Named validation rule attached to a contract column."""

    model_config = ConfigDict(extra="forbid")

    name: str
    column: str
    check: str
    value: float | int | str | None = None


class Contract(BaseModel):
    """Data contract describing expectations for a registered table."""

    model_config = ConfigDict(extra="forbid")

    table: str
    version: str
    columns: dict[str, ContractColumn]
    rules: list[ContractRule] = Field(default_factory=list)
    owner: str | None = None
    description: str | None = None


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
