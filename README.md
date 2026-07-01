# ChangeGuard

A local-first data platform change safety checker for schema changes, data contracts, lineage impact analysis, migration planning, and audit logs.

> **Rules decide. AI explains.** ChangeGuard is a change safety checker, not an AI chatbot.

## Overview

ChangeGuard validates proposed schema or contract changes against metadata, contracts, and lineage **before** those changes are applied. It returns a structured review:

```text
Decision: ALLOW / WARN / BLOCK
Risk Level: LOW / MEDIUM / HIGH / CRITICAL
Checks, impacted assets, migration plan, rollback notes, audit log
```

The tool helps answer: **Can this data platform change be made safely, and what might break downstream?**

## Why ChangeGuard

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

Orion helps you **understand** the platform. ChangeGuard helps you **decide whether a change is safe** before it lands. See [docs/ai_boundary.md](docs/ai_boundary.md).

## Features

- **Structured change requests** from YAML files or CLI flags
- **Table registry** with schema, contract, and lineage metadata pointers
- **Contract validation** for add, rename, drop, and type changes
- **Lineage impact analysis** for downstream tables and dashboards
- **Decision engine** with deterministic `ALLOW` / `WARN` / `BLOCK` aggregation
- **Migration plans** for risky renames, drops, and required column adds
- **Audit logs** saved to `.changeguard/runs/` with replay via `runs` and `review-run`
- **Optional explanations** via `explain-run` without changing the review decision
- **Local-first CLI** — no database connection or cloud dependency required

## Quickstart

### Install

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
changeguard --help
```

### Run the demo

```bash
./examples/demo_workflow.sh
```

Or step through manually:

```bash
changeguard init

changeguard register-table \
  --name sales \
  --schema examples/schemas/sales_schema.json \
  --contract examples/contracts/sales_contract.yml \
  --lineage examples/lineage/sample_lineage.yml

changeguard impact sales.amount

changeguard propose \
  --file examples/change_requests/allow_add_nullable_column.yml

changeguard propose \
  --file examples/change_requests/block_rename_required_column.yml

changeguard runs
changeguard review-run 000001
changeguard explain-run 000001
```

See [docs/demo_transcript.md](docs/demo_transcript.md) for a full walkthrough with expected output.

## Example Review Output

### Allowed change — add nullable column

```bash
changeguard propose --file examples/change_requests/allow_add_nullable_column.yml
```

```text
Decision
ALLOW

Risk Level
LOW

Checks
- [PASS] (contract) Adding nullable column promo_code is allowed by contract

Audit Log
.changeguard/runs/000001.json
```

### Blocked change — rename required downstream column

```bash
changeguard propose --file examples/change_requests/block_rename_required_column.yml
```

```text
Decision
BLOCK

Risk Level
CRITICAL

Checks
- [FAIL] (contract) Column amount is required by contract for table sales
- [FAIL] (lineage) Column amount is referenced by downstream assets: mart_daily_revenue.total_amount, sales_dashboard.revenue_kpi

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

### Example requests

| File | Expected outcome |
|------|------------------|
| `examples/change_requests/allow_add_nullable_column.yml` | ALLOW |
| `examples/change_requests/warn_drop_optional_column.yml` | WARN |
| `examples/change_requests/block_rename_required_column.yml` | BLOCK |

## Architecture

| Component | Role | Module |
|-----------|------|--------|
| Change request parser | Load YAML or CLI flags into structured proposals | `changes.py` |
| Metadata registry | Index tables and metadata file paths | `registry.py`, `workspace.py` |
| Contract checker | Validate proposals against data contracts | `contracts.py` |
| Lineage impact analyzer | Find downstream assets affected by changes | `lineage.py` |
| Decision engine | Aggregate checks into decision and risk level | `rules.py` |
| Migration planner | Generate safe rollout steps | `planner.py` |
| Audit logger | Persist review runs | `audit.py` |
| Optional explanation layer | Summarize saved reviews | `explain.py`, `llm.py` |

```text
Change Request → Parser → Registry → Contract + Lineage checks
      → Decision engine → Migration planner → Audit logger → Explanation layer
```

Workspace layout:

```text
.changeguard/
├── config.json
├── registry.json
└── runs/
    └── 000001.json
```

Full design: [docs/system_design.md](docs/system_design.md)

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 0–7 | Core review pipeline, migration plans, audit logs | Done |
| 8 | CLI polish and example workflows | Done |
| 9 | Optional AI explanation layer | Done |
| 10 | Portfolio packaging | In progress |

## Limitations

ChangeGuard is a **pre-change review** tool. It does not:

- Apply DDL or execute migrations on live databases
- Parse arbitrary SQL migration scripts
- Replace a distributed metadata catalog service
- Require an LLM for core safety decisions

See [docs/limitations.md](docs/limitations.md) and [docs/troubleshooting.md](docs/troubleshooting.md).

## Documentation

| Doc | Description |
|-----|-------------|
| [demo_transcript.md](docs/demo_transcript.md) | Step-by-step demo session |
| [resume_summary.md](docs/resume_summary.md) | Resume and interview bullets |
| [system_design.md](docs/system_design.md) | Architecture and workspace design |
| [ai_boundary.md](docs/ai_boundary.md) | AI safety boundary |
| [decision_rules.md](docs/decision_rules.md) | ALLOW / WARN / BLOCK rules |
| [limitations.md](docs/limitations.md) | MVP boundaries |
| [troubleshooting.md](docs/troubleshooting.md) | Common issues |

## License

TBD
