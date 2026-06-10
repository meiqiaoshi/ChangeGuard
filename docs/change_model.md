# Change Request Model

ChangeGuard accepts structured change proposals describing a single intended modification to a table schema or contract. Requests can be submitted via CLI flags or YAML files.

## Supported Change Types

| Change type | Description |
|-------------|-------------|
| `add_column` | Add a new column to a table |
| `rename_column` | Rename an existing column |
| `drop_column` | Remove a column |
| `change_column_type` | Change a column's data type |
| `set_nullable` | Change nullability (nullable ↔ required) |
| `add_contract_rule` | Add a new rule to the data contract |
| `remove_contract_rule` | Remove a contract rule |
| `tighten_contract_rule` | Make a contract constraint stricter |
| `relax_contract_rule` | Relax a contract constraint |

---

## add_column

Add a new column to a registered table.

**Required fields:** `change_type`, `table`, `column`, `type`, `nullable`

**Example YAML:**

```yaml
change_type: add_column
table: sales
column: discount
type: float
nullable: true
description: Promotional discount applied to the order
```

**Expected risk profile:** LOW when nullable; MEDIUM to HIGH when required without default.

**Possible outcomes:** ALLOW (nullable), WARN or BLOCK (required without backfill plan).

---

## rename_column

Rename an existing column.

**Required fields:** `change_type`, `table`, `column`, `new_name`

**Example YAML:**

```yaml
change_type: rename_column
table: sales
column: amount
new_name: order_amount
description: Align column name with downstream mart naming
```

**Expected risk profile:** MEDIUM if unused; HIGH if referenced by contract, lineage, or quality rules.

**Possible outcomes:** WARN (unused column), BLOCK (used downstream or in contract).

---

## drop_column

Remove a column from a table.

**Required fields:** `change_type`, `table`, `column`

**Example YAML:**

```yaml
change_type: drop_column
table: sales
column: legacy_flag
description: Remove deprecated flag after migration window
```

**Expected risk profile:** MEDIUM for optional unused columns; HIGH or CRITICAL for used or required columns.

**Possible outcomes:** WARN (optional, no dependents), BLOCK (required or referenced).

---

## change_column_type

Change a column's declared type.

**Required fields:** `change_type`, `table`, `column`, `new_type`

**Example YAML:**

```yaml
change_type: change_column_type
table: sales
column: quantity
new_type: bigint
description: Widen quantity to support larger orders
```

**Expected risk profile:** WARN for widening; HIGH for narrowing or incompatible casts.

**Possible outcomes:** WARN (compatible widening), BLOCK (narrowing or contract mismatch).

---

## set_nullable

Change whether a column accepts null values.

**Required fields:** `change_type`, `table`, `column`, `nullable`

**Example YAML:**

```yaml
change_type: set_nullable
table: sales
column: customer_id
nullable: false
description: Enforce customer_id on all new rows
```

**Expected risk profile:** WARN when relaxing to nullable; HIGH when tightening without validation.

**Possible outcomes:** WARN (relax nullable true), BLOCK (tighten nullable false without proof).

---

## add_contract_rule

Add a new validation rule to the table contract.

**Required fields:** `change_type`, `table`, `rule_name`, `rule_definition`

**Example YAML:**

```yaml
change_type: add_contract_rule
table: sales
rule_name: amount_non_negative
rule_definition:
  column: amount
  check: min_value
  value: 0
```

**Expected risk profile:** LOW to MEDIUM depending on whether existing data satisfies the new rule.

**Possible outcomes:** ALLOW or WARN if rule is additive; BLOCK if rule would fail on current schema assumptions.

---

## remove_contract_rule

Remove an existing contract rule.

**Required fields:** `change_type`, `table`, `rule_name`

**Example YAML:**

```yaml
change_type: remove_contract_rule
table: sales
rule_name: legacy_status_check
description: Retire obsolete status enumeration check
```

**Expected risk profile:** LOW to MEDIUM; relaxing governance may WARN downstream consumers.

**Possible outcomes:** ALLOW or WARN.

---

## tighten_contract_rule

Make an existing contract constraint stricter.

**Required fields:** `change_type`, `table`, `rule_name`, `rule_definition`

**Example YAML:**

```yaml
change_type: tighten_contract_rule
table: sales
rule_name: amount_range
rule_definition:
  column: amount
  check: max_value
  value: 100000
```

**Expected risk profile:** MEDIUM to HIGH; may BLOCK if current metadata implies broader allowance.

**Possible outcomes:** WARN or BLOCK.

---

## relax_contract_rule

Relax an existing contract constraint.

**Required fields:** `change_type`, `table`, `rule_name`, `rule_definition`

**Example YAML:**

```yaml
change_type: relax_contract_rule
table: sales
rule_name: amount_range
rule_definition:
  column: amount
  check: max_value
  value: 1000000
```

**Expected risk profile:** LOW to MEDIUM.

**Possible outcomes:** ALLOW or WARN.

---

## Common Fields

All change requests may include:

| Field | Required | Description |
|-------|----------|-------------|
| `change_type` | Yes | One of the supported types above |
| `table` | Yes | Registered table name |
| `description` | No | Human-readable intent |
| `requested_by` | No | Author or team (for audit) |

Validation rejects unknown change types and missing required fields before review runs.
