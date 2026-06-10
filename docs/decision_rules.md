# Change Decision Rules

ChangeGuard uses deterministic rules to map check results to a final decision. This document defines the initial rule matrix for MVP. The rule engine in `rules.py` implements aggregation; individual checks in `contracts.py` and `lineage.py` produce PASS / WARN / FAIL per check.

## Aggregation Rules

```text
Any FAIL  → BLOCK
Any WARN and no FAIL → WARN
All PASS  → ALLOW
```

## Change-Type Rule Matrix

### add_column

| Scenario | Decision | Explanation |
|----------|----------|-------------|
| Add nullable column | ALLOW | No breaking change to existing rows or contracts |
| Add required column without default | WARN or BLOCK | Existing rows would violate NOT NULL unless backfilled |

### rename_column

| Scenario | Decision | Explanation |
|----------|----------|-------------|
| Rename unused column | WARN | Low immediate risk, but name change may confuse operators |
| Rename column used in contract, lineage, or quality rules | BLOCK | Downstream references still point to old name |

### drop_column

| Scenario | Decision | Explanation |
|----------|----------|-------------|
| Drop unused optional column | WARN | Confirm no hidden dependencies before production |
| Drop column referenced downstream or required by contract | BLOCK | Would break dependents or violate contract |

### change_column_type

| Scenario | Decision | Explanation |
|----------|----------|-------------|
| Widening conversion (e.g. int → bigint) | WARN | Usually safe but verify downstream casts |
| Narrowing or incompatible type change | BLOCK | Risk of data loss or parse failures |

### set_nullable

| Scenario | Decision | Explanation |
|----------|----------|-------------|
| Relax nullable (required → nullable) | WARN | Weakens guarantees; downstream may assume non-null |
| Tighten nullable (nullable → required) | BLOCK unless validated | Existing nulls would violate new constraint |

### Contract rule changes

| Scenario | Decision | Explanation |
|----------|----------|-------------|
| add_contract_rule | ALLOW or WARN | Depends on whether current schema satisfies new rule |
| remove_contract_rule | ALLOW or WARN | Relaxes governance |
| tighten_contract_rule | WARN or BLOCK | Stricter constraint may fail on existing data |
| relax_contract_rule | ALLOW or WARN | Generally lower risk |

## Risk Level Mapping

| Decision context | Risk level |
|------------------|------------|
| ALLOW, simple nullable add | LOW |
| WARN, optional column or no lineage hits | MEDIUM |
| BLOCK, contract violation | HIGH |
| BLOCK, downstream production-critical asset | CRITICAL (optional tag) |

Risk levels inform migration plan urgency and CLI display order; they do not override the ALLOW / WARN / BLOCK decision.

## Check Sources

| Source module | Examples |
|---------------|----------|
| Contract checks | Required column drop, type mismatch, rule reference |
| Lineage checks | Downstream column reference on rename/drop |
| Quality rules | Rule depends on renamed or dropped column |
| Schema validation | Unknown table, duplicate column name |

## Non-Goals for MVP Rules

- No ML-based risk scoring
- No environment-specific overrides (dev vs prod)
- No automatic approval workflows

Rules are versioned in Git via this document and test fixtures; changes to the matrix should add or update pytest cases in Phase 5.
