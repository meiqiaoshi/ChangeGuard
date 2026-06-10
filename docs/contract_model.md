# Data Contract Model

ChangeGuard data contracts are simple YAML files that describe expectations for a registered table. Contracts are loaded during review to detect violations when a proposed change would break published guarantees.

## File Structure

```yaml
table: sales
version: "1.0"
owner: analytics-team
description: Core sales fact table contract

columns:
  order_id:
    type: string
    required: true
    unique: true
    primary_key: true

  amount:
    type: float
    required: true
    min_value: 0

  customer_id:
    type: string
    required: true

  order_date:
    type: date
    required: true

rules:
  - name: amount_non_negative
    column: amount
    check: min_value
    value: 0

  - name: valid_order_dates
    column: order_date
    check: not_null
```

## Column Fields

| Field | Description |
|-------|-------------|
| `type` | Logical type: string, int, float, date, timestamp, boolean, etc. |
| `required` | If true, column must exist and be non-null per contract |
| `nullable` | Alternative to required; `nullable: false` implies required |
| `unique` | Hint that values should be unique (informational for review) |
| `primary_key` | Marks primary key column(s) |
| `allowed_values` | List of permitted enum values |
| `min_value` / `max_value` | Numeric range bounds |
| `pattern` | Optional string regex pattern |

## Rule Fields

Contract rules are named checks attached to columns:

| Check | Meaning |
|-------|---------|
| `not_null` | Column must not contain nulls |
| `min_value` / `max_value` | Numeric bounds |
| `allowed_values` | Enum membership |
| `unique` | Uniqueness expectation |

Rules are referenced by name during tighten/relax/remove change types.

## How Contracts Are Used in Review

1. **add_column** — New column must not conflict with existing names; required columns without defaults trigger WARN/BLOCK.
2. **rename_column** — Renaming a contract-required column triggers BLOCK unless migration plan exists.
3. **drop_column** — Dropping a required or rule-referenced column triggers BLOCK.
4. **change_column_type** — New type must remain compatible with contract type and rules.
5. **set_nullable** — Tightening nullability on a required column may BLOCK without validation evidence.

## Design Constraints

- Contracts are **declarative YAML**, not executable code.
- No SQL or Python embedded in contract files for MVP.
- Freshness expectations (SLA, max staleness) may be added in a later phase.
- One contract file per table, referenced from the registry.

## Example Location

See `examples/contracts/sales_contract.yml` for a minimal working contract used in demos and tests.
