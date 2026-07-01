# ChangeGuard Limitations

ChangeGuard is a local-first **pre-change review** tool. It helps teams decide whether a proposed schema or contract change is safe before it is applied. It does not execute changes on your behalf.

This document describes intentional MVP boundaries and known gaps.

## No Live Database Changes

ChangeGuard does not connect to production databases, warehouses, or lakehouse catalogs to apply DDL. It reads local metadata files referenced by the workspace registry and evaluates proposed changes against those files.

Implications:

- Review results describe **expected** safety based on registered contracts and lineage, not live runtime state.
- A change marked `ALLOW` still requires your normal deployment and validation process.
- Schema drift between registered metadata and the real table is not detected automatically.

## No Automatic Destructive Operations

ChangeGuard never drops columns, renames fields, or mutates contracts on its own. Even when a change is `BLOCK`, the tool only reports reasons, migration guidance, and rollback notes.

Implications:

- Operators must execute migration steps manually or through separate tooling.
- Deprecation windows and backfills are recommendations, not enforced workflows.

## No Complete SQL Parser

ChangeGuard accepts structured change requests from YAML files or CLI flags. It does not parse arbitrary SQL migration scripts, dbt model diffs, or ORM migration files.

Implications:

- Complex multi-table migrations must be broken into individual change requests.
- Implicit SQL-side effects (views, triggers, stored procedures) are out of scope unless modeled in lineage metadata.

## No Distributed Metadata Service

ChangeGuard stores workspace state locally under `.changeguard/`. There is no central metadata server, multi-user locking, or cross-repo registry sync.

Implications:

- Each clone or machine maintains its own registry and audit log unless you commit `.changeguard/` to version control deliberately.
- Team coordination happens through Git and shared metadata files, not through a live catalog API.

## Other MVP Boundaries

| Area | Current behavior |
|------|------------------|
| Web UI | Not provided; CLI only |
| Authentication | Not provided |
| Quality rules | Example files exist; full quality integration is limited |
| AI explanation | Optional future layer; decisions are deterministic today |
| Streaming / real-time lineage | Not supported |
| Contract rule editing | Change types for contract rules are documented but not all are implemented in the MVP CLI |

## What ChangeGuard Is Good For

- Reviewing column add, rename, drop, and type changes before merge or deploy
- Surfacing contract and lineage risk for a single table change
- Generating a structured migration plan and audit trail for team review
- Demonstrating pre-change governance in a portfolio or interview setting

## Related Docs

- [System design](system_design.md)
- [Decision rules](decision_rules.md)
- [Troubleshooting](troubleshooting.md)
- [AI explanation boundary](ai_boundary.md)
