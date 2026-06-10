# ChangeGuard System Design

ChangeGuard is a local-first CLI that reviews proposed data platform changes before they are applied. It loads metadata from the workspace, runs deterministic checks, and produces a structured review result with an optional migration plan and audit log.

## Review Flow

```text
Change Request
      ↓
Metadata Loader
      ↓
Contract Checks + Lineage Checks + Rule Engine
      ↓
Decision + Migration Plan + Audit Log
```

## Workspace Layout

When a user runs `changeguard init`, a local workspace is created:

```text
.changeguard/
├── config.json          # Workspace configuration
├── registry.json        # Registered tables and metadata pointers
└── runs/                # Persisted review runs (audit trail)
    └── 000001.json
```

Source metadata (schemas, contracts, lineage, quality rules) lives in the project repository under `examples/` or user-defined paths referenced by the registry.

## Registry

The registry is the index of known tables. Each entry points to:

- Table name
- Schema file path
- Contract file path (optional)
- Lineage file path (optional)
- Quality rules file path (optional)

The registry does not duplicate full schema content; it references local files so metadata stays inspectable in Git.

## Contracts

Data contracts describe expectations for a table:

- Required columns and types
- Nullability
- Allowed values and numeric ranges
- Uniqueness and primary-key hints

Contract checks run during review to detect whether a proposed change would violate published expectations or break downstream assumptions.

## Lineage Metadata

Lineage files describe dependencies between assets:

- Which columns or tables depend on a source column
- Downstream marts, dashboards, or pipelines (as logical asset names)

Lineage checks answer: **if this column changes or disappears, what else is affected?**

## Change Requests

A change request is a structured proposal, either from CLI flags or a YAML file under `examples/change_requests/`. Supported change types include column add/rename/drop/type changes and contract rule modifications.

Each request is validated for required fields before review begins.

## Rule Engine

The rule engine combines individual check results into a final decision:

| Check outcome | Aggregated decision |
|---------------|---------------------|
| Any FAIL | BLOCK |
| Any WARN, no FAIL | WARN |
| All PASS | ALLOW |

Risk levels (LOW / MEDIUM / HIGH / CRITICAL) are assigned from the change type and severity of failed checks. See `docs/decision_rules.md` for the initial rule matrix.

## Decision Output

A completed review produces a `ReviewResult`:

```text
Decision: ALLOW | WARN | BLOCK
Risk Level: LOW | MEDIUM | HIGH | CRITICAL
Reasons: list of human-readable explanations
Impacted assets: downstream tables, columns, rules
Failed checks: structured check results
Migration plan: ordered steps when change is not directly safe
Rollback notes: how to undo or mitigate
Audit log path: path to persisted run JSON
```

Rendering is handled by `render.py`; persistence by `audit.py`.

## Audit Logs

Every `propose` run can be saved under `.changeguard/runs/` with a monotonic run ID. Users list runs with `changeguard runs` and inspect a past result with `changeguard review-run <id>`.

Audit logs make the review process reproducible and portfolio-friendly: each decision is traceable to inputs and rule outcomes.

## Module Responsibilities

| Module | Role |
|--------|------|
| `cli.py` | Typer commands and user entry points |
| `workspace.py` | Workspace paths and initialization |
| `registry.py` | Table registration and lookup |
| `schema.py` | Schema file loading and validation |
| `contracts.py` | Contract loading and column checks |
| `lineage.py` | Lineage loading and impact lookup |
| `changes.py` | Change request models and YAML loading |
| `rules.py` | Decision aggregation and risk scoring |
| `planner.py` | Orchestrates full review pipeline |
| `audit.py` | Run ID generation and persistence |
| `render.py` | CLI-friendly output formatting |
| `models.py` | Shared Pydantic models |

## Design Principles

1. **Local-first** — JSON/YAML on disk; no cloud or database required for MVP.
2. **Deterministic** — The rule engine makes the safety decision; optional AI only explains later.
3. **Inspectable** — Metadata and audit logs are plain text files suitable for Git review.
4. **Incremental** — Each phase adds one layer (registry → changes → contracts → lineage → decision → audit).
