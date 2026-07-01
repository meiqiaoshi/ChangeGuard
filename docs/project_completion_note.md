# ChangeGuard Project Completion Note

Final summary for portfolio submission, OPT phase notes, and interview preparation.

## What Was Built

ChangeGuard is a local-first CLI that reviews proposed data platform schema changes before they are applied. The MVP includes:

- **Workspace and registry** — `.changeguard/` layout with table metadata pointers
- **Change request model** — YAML and CLI flags for add, rename, drop, and type changes
- **Contract validation** — Required column protection and contract-aware checks
- **Lineage impact analysis** — Downstream asset discovery for column-level changes
- **Decision engine** — Deterministic `ALLOW` / `WARN` / `BLOCK` with risk levels
- **Migration planner** — Safe rollout steps for renames, drops, and required column adds
- **Audit logs** — Persisted review runs with `runs`, `review-run`, and JSON replay
- **Optional explanation layer** — `explain-run` with deterministic fallback (no API key required)
- **Demo and docs** — Example requests, demo script, demo transcript, resume summary, troubleshooting guides
- **Test suite** — 200+ pytest cases covering unit, integration, and end-to-end workflows

Primary CLI commands:

```bash
changeguard init
changeguard register-table
changeguard tables
changeguard inspect
changeguard impact
changeguard propose
changeguard runs
changeguard review-run
changeguard explain-run
```

## What Problems It Solves

Data teams frequently change schemas without a structured pre-change gate that combines:

- Published **data contracts**
- **Lineage** dependencies
- Explicit **risk classification**
- **Migration guidance**
- **Auditable review history**

ChangeGuard addresses this by answering:

```text
Can this change be made safely, and what might break downstream?
```

It is designed for local development, portfolio demos, and governance-minded engineering workflows — not for replacing a full enterprise catalog or executing DDL in production.

## Key Design Decisions

### Rules decide. AI explains.

Safety decisions come only from deterministic checks and aggregation rules. The optional explanation layer summarizes completed reviews; it never overrides `ALLOW`, `WARN`, or `BLOCK`.

### Local-first and inspectable

Metadata lives in Git-tracked YAML/JSON files. Review runs are saved as readable JSON under `.changeguard/runs/`. No cloud service is required for the core workflow.

### Registry as an index, not a warehouse

The registry stores pointers to schema, contract, and lineage files rather than duplicating full metadata content. This keeps reviews reproducible and easy to inspect.

### Structured change requests over SQL parsing

Changes are submitted as explicit proposals (YAML or flags), not parsed from arbitrary SQL migration scripts. This keeps the MVP focused and testable.

### Fail-safe aggregation

```text
Any FAIL  → BLOCK
Any WARN  → WARN (if no FAIL)
All PASS  → ALLOW
```

Risk levels provide urgency context but do not override the decision.

## Limitations

- Does not connect to live databases or apply schema changes
- Does not parse full SQL migration files or dbt diffs
- No distributed metadata service or multi-user coordination layer
- No web UI or authentication
- Quality rules are example-level; full SentinelDQ-style integration is not implemented
- OpenAI-compatible LLM adapter is a placeholder; explanations use deterministic templates in the MVP

See [limitations.md](limitations.md) for the full list.

## Future Improvements

- Wire `OpenAICompatibleClient` to a real API with strict read-only review input
- Integrate quality-rule checks from metadata files into the planner
- Support contract rule change types in the CLI
- Parse common SQL DDL patterns into structured change requests
- Add workspace-level policy packs (team-specific decision thresholds)
- Export review results to Markdown/PDF for change advisory boards
- Optional catalog adapter for pulling lineage from an external system

## Resume Positioning

**One-line summary:**

ChangeGuard is a local-first data platform change safety checker that reviews proposed schema changes against data contracts and lineage metadata before they are applied.

**Primary resume bullet:**

Built ChangeGuard, a local-first data platform change safety checker that validates proposed schema changes against data contracts and lineage metadata, classifies risk, blocks unsafe operations, and generates auditable migration plans.

**Portfolio story with related projects:**

```text
LakeTable   -> storage-layer table behavior
LineageHub  -> metadata and downstream impact
ChangeGuard -> pre-change governance and safety review
Orion       -> AI-assisted metadata understanding (separate concern)
```

ChangeGuard demonstrates **governance and change safety**, complementing storage and catalog projects rather than duplicating them.

## Verification Checklist

The MVP is complete when these all pass:

```bash
pip install -e ".[dev]"
pytest
./examples/demo_workflow.sh
changeguard propose --file examples/change_requests/block_rename_required_column.yml
changeguard runs
changeguard explain-run 000001
```

## Related Docs

- [README](../README.md)
- [Resume summary](resume_summary.md)
- [Demo transcript](demo_transcript.md)
- [System design](system_design.md)
- [AI boundary](ai_boundary.md)
