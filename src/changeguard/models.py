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


class CheckStatus(str, Enum):
    """Result status for an individual safety check."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class CheckResult(BaseModel):
    """Structured result from a single contract, lineage, or rule check."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: CheckStatus
    message: str
    source: str = "contract"


class Decision(str, Enum):
    """Final review decision for a proposed change."""

    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"


class RiskLevel(str, Enum):
    """Risk level assigned to a review result."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MigrationStep(BaseModel):
    """Single step in a recommended safe migration plan."""

    model_config = ConfigDict(extra="forbid")

    step_number: int
    title: str
    description: str
    required: bool
    validation_hint: str | None = None


class MigrationPlan(BaseModel):
    """Ordered migration plan for applying a change safely."""

    model_config = ConfigDict(extra="forbid")

    steps: list[MigrationStep] = Field(default_factory=list)


class ReviewResult(BaseModel):
    """Structured output from a completed change review."""

    model_config = ConfigDict(extra="forbid")

    decision: Decision
    risk_level: RiskLevel
    reasons: list[str] = Field(default_factory=list)
    check_results: list[CheckResult] = Field(default_factory=list)
    impacted_assets: list[str] = Field(default_factory=list)
    migration_plan: MigrationPlan | None = None
    rollback_notes: list[str] = Field(default_factory=list)


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


class AssetType(str, Enum):
    """Supported asset types referenced in lineage metadata."""

    TABLE = "table"
    COLUMN = "column"
    MART = "mart"
    DASHBOARD = "dashboard"
    QUALITY_RULE = "quality_rule"
    CONTRACT = "contract"


class AssetRef(BaseModel):
    """Reference to a logical data platform asset."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str
    asset_type: AssetType = Field(alias="type")
    column: str | None = None


class LineageEdge(BaseModel):
    """Directed dependency between two assets."""

    model_config = ConfigDict(extra="forbid")

    source: AssetRef
    target: AssetRef
    source_column: str | None = None
    target_column: str | None = None


class LineageGraph(BaseModel):
    """Graph of lineage assets and dependency edges."""

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0"
    assets: list[AssetRef] = Field(default_factory=list)
    edges: list[LineageEdge] = Field(default_factory=list)


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
