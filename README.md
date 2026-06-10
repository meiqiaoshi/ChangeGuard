# ChangeGuard

A local-first data platform change safety checker for schema changes, data contracts, lineage impact analysis, migration planning, and audit logs.

## One-Sentence Summary

ChangeGuard validates proposed schema or contract changes against metadata, contracts, and lineage **before** those changes are applied — and tells you whether the change is safe and what might break downstream.

> **ChangeGuard is a change safety checker, not an AI chatbot.**

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

Core principle: **Rules decide. AI explains.** (Any AI explanation layer is optional and comes later.)

## Core Workflow Preview

```bash
changeguard init

changeguard register-table \
  --name sales \
  --schema examples/schemas/sales_schema.json \
  --contract examples/contracts/sales_contract.yml

changeguard tables
changeguard inspect sales

changeguard propose \
  --change-type add_column \
  --table sales \
  --column discount \
  --type float \
  --nullable true

changeguard propose \
  --change-type rename_column \
  --table sales \
  --column amount \
  --new-name order_amount

changeguard impact sales.amount
changeguard runs
changeguard review-run 000001
```

Example review output:

```text
Decision: BLOCK
Risk Level: HIGH

Reason:
- sales.amount is required by sales_contract.yml
- sales.amount is referenced by mart_daily_revenue.total_amount
- quality rule sales_amount_positive depends on sales.amount

Safe Migration Plan:
1. Add order_amount as a new nullable column
2. Backfill order_amount from amount
3. Update downstream assets
4. Run contract checks
5. Run quality checks
6. Deprecate amount after compatibility window
```

## Non-Goals

The initial version intentionally avoids:

- Web UI
- Live production database changes or automatic execution of destructive changes
- Distributed service or cloud dependency
- Authentication
- Complex SQL parser or full dbt replacement
- Real-time streaming integration
- LLM required for MVP

ChangeGuard stays a clean, local-first, inspectable CLI tool.

## Initial Roadmap

| Phase | Focus |
|-------|-------|
| 0 | Documentation and project scaffold |
| 1 | Workspace and table registry MVP |
| 2 | Change request model |
| 3 | Contract validation |
| 4 | Lineage impact analysis |
| 5 | Decision engine (`ALLOW` / `WARN` / `BLOCK`) |
| 6 | Migration plan generator |
| 7 | Audit log and run review |
| 8 | CLI polish and example workflows |
| 9 | Optional AI explanation layer |
| 10 | Portfolio packaging |

## License

TBD
