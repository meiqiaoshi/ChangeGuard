# ChangeGuard

A local-first data platform change safety checker for schema changes, data contracts, lineage impact analysis, migration planning, and audit logs.

ChangeGuard validates proposed schema or contract changes against metadata, contracts, and lineage **before** those changes are applied — and tells you whether the change is safe and what might break downstream.

> **ChangeGuard is a change safety checker, not an AI chatbot.** Rules decide. AI explains.

## Installation

From a clean checkout:

```bash
git clone <repo-url>
cd ChangeGuard
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv sync --dev
```

Verify the CLI:

```bash
changeguard --help
```

## Quickstart

Run the full demo in a temporary workspace:

```bash
./examples/demo_workflow.sh
```

Or follow these steps manually from the repository root:

```bash
changeguard init

changeguard register-table \
  --name sales \
  --schema examples/schemas/sales_schema.json \
  --contract examples/contracts/sales_contract.yml \
  --lineage examples/lineage/sample_lineage.yml

changeguard tables
changeguard inspect sales
changeguard impact sales.amount
```

## Example Allowed Change

Propose adding a nullable column:

```bash
changeguard propose \
  --file examples/change_requests/allow_add_nullable_column.yml
```

Example output:

```text
Change Request
change_type: add_column
table: sales
column: promo_code
...

Decision
ALLOW

Risk Level
LOW

Checks
- [PASS] (contract) Adding nullable column promo_code is allowed by contract

Audit Log
.changeguard/runs/000001.json
```

## Example Blocked Change

Propose renaming a required downstream column:

```bash
changeguard propose \
  --file examples/change_requests/block_rename_required_column.yml
```

Example output:

```text
Decision
BLOCK

Risk Level
CRITICAL

Checks
- [FAIL] (contract) Column amount is required by contract for table sales
- [FAIL] (lineage) Column amount is referenced by downstream assets: ...

Impacted Assets
- mart_daily_revenue.total_amount
- sales_dashboard.revenue_kpi

Migration Plan
1. Add new column as nullable
2. Backfill new column from old column
3. Update downstream assets
4. Run contract checks
5. Run quality checks
6. Deprecate old column after compatibility window

Rollback Notes
- Keep old column until downstream validation passes
- Do not delete old data files
- Restore previous contract version if checks fail
```

Other example requests:

| File | Expected outcome |
|------|------------------|
| `examples/change_requests/allow_add_nullable_column.yml` | ALLOW |
| `examples/change_requests/warn_drop_optional_column.yml` | WARN |
| `examples/change_requests/block_rename_required_column.yml` | BLOCK |

## Audit Log Example

Every successful `propose` run is saved under `.changeguard/runs/`:

```bash
changeguard runs
changeguard review-run 000001
```

Example run listing:

```text
run_id  decision  risk_level  change_type     target           created_at
000001  ALLOW     LOW         add_column      sales.promo_code 2026-06-29T...
000002  BLOCK     CRITICAL    rename_column   sales.amount     2026-06-29T...
```

Each audit JSON file stores the decision, checks, migration plan, rollback notes, and change metadata for later inspection.

## Optional AI Explanation

ChangeGuard includes an optional explanation layer for saved review runs. The rule engine still makes every safety decision. The explanation layer only summarizes the result in plain language.

```bash
changeguard explain-run 000001
```

Typical workflow:

```bash
changeguard propose --file examples/change_requests/block_rename_required_column.yml
changeguard review-run 000001
changeguard explain-run 000001
```

Example output:

```text
This change received a BLOCK decision with CRITICAL risk.
The proposed change failed one or more safety checks and should not be applied as requested.

Key concerns:
- Column amount is required by contract for table sales
- Column amount is referenced by downstream assets: mart_daily_revenue.total_amount

Recommended migration approach:
1. Add new column as nullable
2. Backfill new column from old column
```

Adapter options in `src/changeguard/llm.py`:

| Client | Behavior |
|--------|----------|
| `NoOpLLMClient` | Deterministic template explanation (default-compatible) |
| `OpenAICompatibleClient` | Placeholder for future OpenAI-compatible APIs; falls back to deterministic text in the MVP |

No API key is required for tests or local demos. See [docs/ai_boundary.md](docs/ai_boundary.md) for the safety boundary.

## Project Architecture

```text
Change Request
      ↓
Metadata Loader (registry, contracts, lineage)
      ↓
Contract Checks + Lineage Checks + Rule Engine
      ↓
Decision + Migration Plan + Audit Log
      ↓
Optional Explanation Layer
```

Workspace layout:

```text
.changeguard/
├── config.json
├── registry.json
└── runs/
    └── 000001.json
```

Source metadata lives in the repository under `examples/` or user-defined paths referenced by the registry. See [docs/system_design.md](docs/system_design.md) for the full design.

## Why This Project Exists

Most data incidents do not happen because someone cannot write SQL. They happen because someone changes a schema, drops a field, renames a column, tightens a contract, or modifies pipeline output without knowing what depends on it.

ChangeGuard fills the **pre-change safety review** gap in a local data platform stack:

| Layer | Example Project | Role |
|-------|-----------------|------|
| ETL & marts | NYC Taxi ETL | Batch pipelines and analytical marts |
| Data quality | SentinelDQ | Profiling and quality rules |
| Lineage & catalog | LineageHub | Impact analysis and metadata |
| AI copilot | Orion | Understand data and ask metadata/query questions |
| Storage | LakeTable | Snapshots, time travel, compaction |
| **Change safety** | **ChangeGuard** | **Review proposed changes before they land** |

## How ChangeGuard Differs from Orion

| | Orion | ChangeGuard |
|---|-------|---------------|
| Purpose | Helps users understand data and ask metadata/query questions | Reviews proposed changes and decides whether they are safe |
| Decision model | Conversational assistance | Deterministic rule engine |
| Output | Natural language answers | `ALLOW` / `WARN` / `BLOCK` with risk level, reasons, and migration plan |
| AI role | Core interaction model | Optional explanation of deterministic results only |

See [docs/ai_boundary.md](docs/ai_boundary.md) for the safety boundary.

## Non-Goals

The initial version intentionally avoids:

- Web UI
- Live production database changes or automatic execution of destructive changes
- Distributed service or cloud dependency
- Authentication
- Complex SQL parser or full dbt replacement
- Real-time streaming integration
- LLM required for core review workflow

ChangeGuard stays a clean, local-first, inspectable CLI tool.

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 0 | Documentation and project scaffold | Done |
| 1 | Workspace and table registry | Done |
| 2 | Change request model | Done |
| 3 | Contract validation | Done |
| 4 | Lineage impact analysis | Done |
| 5 | Decision engine (`ALLOW` / `WARN` / `BLOCK`) | Done |
| 6 | Migration plan generator | Done |
| 7 | Audit log and run review | Done |
| 8 | CLI polish and example workflows | Done |
| 9 | Optional AI explanation layer | Done |
| 10 | Portfolio packaging | Planned |

## License

TBD
