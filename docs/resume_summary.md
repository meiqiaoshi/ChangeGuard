# ChangeGuard Resume Summary

Portfolio-ready summary for resumes, LinkedIn, and interview prep.

## One-Line Summary

ChangeGuard is a local-first data platform change safety checker that reviews proposed schema changes against data contracts and lineage metadata before they are applied.

## Technical Highlights

- **Deterministic review engine** — Aggregates contract and lineage checks into `ALLOW`, `WARN`, or `BLOCK` with risk levels (`LOW` through `CRITICAL`)
- **Structured change requests** — YAML or CLI flags for add, rename, drop, and type changes
- **Contract validation** — Protects required columns and published table expectations
- **Lineage impact analysis** — Surfaces downstream tables and dashboards affected by column changes
- **Migration planning** — Generates safe rollout steps for renames, drops, and required column adds
- **Audit trail** — Persists every review under `.changeguard/runs/` with replay via `runs` and `review-run`
- **Optional explanation layer** — Plain-language summaries via `explain-run` without changing the rule-engine decision
- **Local-first CLI** — No database connection, no cloud dependency, no API key required for core workflows
- **Test-driven MVP** — 200+ pytest cases covering contracts, lineage, decisions, migration plans, audit logs, and demo workflow

## Resume Bullets

Use one or two of these depending on space:

**Primary bullet (recommended):**

Built ChangeGuard, a local-first data platform change safety checker that validates proposed schema changes against data contracts and lineage metadata, classifies risk, blocks unsafe operations, and generates auditable migration plans.

**Alternate bullets:**

- Designed a deterministic change review pipeline that combines contract checks, lineage impact analysis, and rule-based decision aggregation for schema change proposals.
- Implemented a CLI workflow with structured audit logs, migration plan generation, and optional AI explanation layered on top of fixed safety decisions.
- Built a metadata-driven governance tool that turns proposed column renames and drops into actionable `BLOCK` / `WARN` / `ALLOW` reviews with downstream impact visibility.

## Interview Talking Points

1. **Problem framing** — Schema changes are easy to make but hard to make safely. Teams often lack a pre-change gate that combines contracts, lineage, and explicit risk classification.

2. **Design principle** — *Rules decide. AI explains.* The decision engine is deterministic. Any AI layer only summarizes results already computed by rules and metadata.

3. **Walk through a blocked rename** — Renaming `sales.amount` fails contract checks (required column) and lineage checks (referenced by `mart_daily_revenue` and `sales_dashboard`). Output includes impacted assets, a six-step migration plan, rollback notes, and a saved audit log.

4. **Why local-first** — Metadata lives in Git-tracked YAML/JSON. Reviews are reproducible, inspectable, and demo-friendly without standing up a platform service.

5. **Extensibility** — Registry points to external schema, contract, and lineage files. New change types and checks can be added without rewriting the CLI surface.

6. **What you would add next** — Live catalog integration, quality-rule checks in the planner, SQL migration parsing, or a wired OpenAI-compatible explanation adapter.

## How It Differs from Orion

| | Orion | ChangeGuard |
|---|-------|-------------|
| Primary job | Help users understand data and ask metadata/query questions | Review proposed changes before they are applied |
| Interaction model | Conversational AI copilot | Structured CLI review workflow |
| Output | Natural language answers | `ALLOW` / `WARN` / `BLOCK`, risk level, checks, migration plan, audit log |
| Who decides safety | User judgment assisted by AI | Deterministic rule engine |
| Role of AI | Core to the product experience | Optional explanation of an already computed result |

Orion helps you **understand** the platform. ChangeGuard helps you **decide whether a change is safe** before it lands.

## How It Complements LakeTable and LineageHub

**LakeTable** focuses on storage-layer table internals: snapshots, time travel, compaction, and how analytical tables behave at the file/format level. ChangeGuard does not implement storage engines. It assumes tables exist and asks whether a proposed schema change is safe against published expectations and dependencies.

**LineageHub** focuses on metadata, cataloging, and impact analysis across assets. ChangeGuard reuses that same lineage mindset at review time: when a column is renamed or dropped, downstream marts and dashboards must be considered before approval. ChangeGuard turns lineage metadata into a hard gate in the change workflow, not just an exploration view.

Together in a portfolio story:

```text
LakeTable   -> how tables are stored and versioned
LineageHub  -> what depends on what
ChangeGuard -> whether a proposed change is safe before apply
```

ChangeGuard sits at the **governance and pre-change safety** layer above storage and catalog concerns.

## Elevator Pitch (30 seconds)

"I built ChangeGuard to model a common data platform problem: schema changes are easy to make but hard to make safely. The tool accepts proposed changes like renaming or dropping a column, validates them against data contracts and lineage dependencies, assigns ALLOW, WARN, or BLOCK, and generates a migration plan with an audit log. The key design choice is that deterministic rules make the safety decision, while an optional explanation layer can describe the result in plain language."

## Related Docs

- [README](../README.md)
- [System design](system_design.md)
- [AI explanation boundary](ai_boundary.md)
- [Decision rules](decision_rules.md)
