# ChangeGuard Demo Transcript

Example session for portfolio demos and interview walkthroughs. Commands assume you are in the **ChangeGuard repository root** with the package installed (`pip install -e ".[dev]"` or `uv sync --dev`).

For a one-command demo, you can also run:

```bash
./examples/demo_workflow.sh
```

The transcript below shows the same workflow step by step with expected output.

---

## 1. Initialize workspace

```bash
mkdir demo-workspace && cd demo-workspace
changeguard init
```

```text
Initialized ChangeGuard workspace at .changeguard
```

---

## 2. Register the sales table

```bash
changeguard register-table \
  --name sales \
  --schema ../examples/schemas/sales_schema.json \
  --contract ../examples/contracts/sales_contract.yml \
  --lineage ../examples/lineage/sample_lineage.yml
```

```text
Registered table: sales
```

---

## 3. Explore registered metadata

```bash
changeguard tables
changeguard inspect sales
```

```text
sales
```

```text
name: sales
schema path: .../examples/schemas/sales_schema.json
contract path: .../examples/contracts/sales_contract.yml
owner: (none)
tags: (none)
description: (none)
```

---

## 4. Check downstream impact

```bash
changeguard impact sales.amount
```

```text
Impacted assets for sales.amount:
- mart_daily_revenue (table) column: total_amount
- sales_dashboard (dashboard) column: revenue_kpi
```

---

## 5. Propose an allowed change

```bash
changeguard propose \
  --file ../examples/change_requests/allow_add_nullable_column.yml
```

```text
Change Request
change_type: add_column
table: sales
column: promo_code
type: string
nullable: true
description: Add optional promo code column for campaign tracking

Decision
ALLOW

Risk Level
LOW

Checks
- [PASS] (contract) Adding nullable column promo_code is allowed by contract

Impacted Assets
(none)

Reasons
(none)

Audit Log
.changeguard/runs/000001.json
```

---

## 6. Propose a blocked change

```bash
changeguard propose \
  --file ../examples/change_requests/block_rename_required_column.yml
```

```text
Change Request
change_type: rename_column
table: sales
column: amount
new_name: order_amount
description: Rename required downstream column amount to order_amount

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

Reasons
- Column amount is required by contract for table sales
- Column amount is referenced by downstream assets: mart_daily_revenue.total_amount, sales_dashboard.revenue_kpi

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

Audit Log
.changeguard/runs/000002.json
```

---

## 7. List saved review runs

```bash
changeguard runs
```

```text
run_id	decision	risk_level	change_type	target	created_at
000001	ALLOW	LOW	add_column	sales.promo_code	2026-07-01T20:43:41.462997+00:00
000002	BLOCK	CRITICAL	rename_column	sales.amount	2026-07-01T20:43:41.590624+00:00
```

Timestamps will differ on each run.

---

## 8. Replay a saved review

```bash
changeguard review-run 000001
```

```text
Decision
ALLOW

Risk Level
LOW

Checks
- [PASS] (contract) Adding nullable column promo_code is allowed by contract

Impacted Assets
(none)

Reasons
(none)
```

---

## 9. Explain a saved review in plain language

```bash
changeguard explain-run 000001
```

```text
This change received a ALLOW decision with LOW risk.
The proposed change passed all safety checks and may proceed with normal deployment practices.
```

For the blocked rename (`000002`), `explain-run` also summarizes key concerns, impacted assets, migration steps, and rollback guidance.

---

## Demo talking points

1. **Allowed change** — Adding a nullable column passes contract checks with low risk.
2. **Blocked change** — Renaming a required downstream column fails both contract and lineage checks.
3. **Migration plan** — ChangeGuard suggests a safe compatibility rollout instead of only saying no.
4. **Audit trail** — Every `propose` run is saved and replayable with `runs`, `review-run`, and `explain-run`.
5. **Safety boundary** — The rule engine decides; the explanation layer only summarizes the result.

## Related docs

- [README](../README.md)
- [Resume summary](resume_summary.md)
- [AI explanation boundary](ai_boundary.md)
