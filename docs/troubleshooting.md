# ChangeGuard Troubleshooting

Common issues when running ChangeGuard locally and how to resolve them.

## Workspace and Registry

### `Table not found: sales`

The table is not registered in the current workspace.

Fix:

```bash
changeguard init
changeguard register-table \
  --name sales \
  --schema examples/schemas/sales_schema.json \
  --contract examples/contracts/sales_contract.yml \
  --lineage examples/lineage/sample_lineage.yml
```

Make sure you run commands from the directory that contains `.changeguard/`, or pass `--path` where supported.

### Contract or lineage checks are missing from review output

ChangeGuard skips checks when metadata is unavailable. If a table is not registered, or contract/lineage paths are missing, the planner returns a permissive result with fewer checks.

Fix:

- Register the table with `--contract` and `--lineage` paths.
- Confirm paths in `changeguard inspect sales` point to existing files.
- Use absolute paths or paths relative to the workspace root when registering.

## Change Requests

### `Provide --file or --change-type with change flags`

`changeguard propose` requires either a YAML file or CLI flags.

Examples:

```bash
changeguard propose --file examples/change_requests/allow_add_nullable_column.yml

changeguard propose \
  --change-type add_column \
  --table sales \
  --column promo_code \
  --type string \
  --nullable true
```

### `Invalid nullable value: ...`

The `--nullable` flag expects `true` or `false` as text, not a bare boolean flag.

```bash
changeguard propose ... --nullable true
```

### YAML validation errors

Change request files must include required fields for the change type. See [change_model.md](change_model.md).

Common mistakes:

- `rename_column` missing `new_name`
- `add_column` missing `type` or `nullable`
- Wrong `change_type` value spelling (use `add_column`, not `add-column`)

## Impact and Lineage

### `No lineage path registered for table: sales`

The `impact` command requires lineage metadata for the target table.

Fix:

```bash
changeguard register-table \
  --name sales \
  ... \
  --lineage examples/lineage/sample_lineage.yml
```

### `No downstream assets impacted by sales.amount`

This is informational, not an error. It means lineage metadata lists no downstream references for that column.

## Audit Logs

### `Review run not found: 000099`

The run ID does not exist under `.changeguard/runs/`.

Fix:

```bash
changeguard runs
changeguard review-run 000001
```

Run IDs are six-digit strings. Unpadded IDs such as `1` are accepted and normalized to `000001`.

### `No review runs saved`

No successful `propose` command has been run in the current workspace yet.

Fix:

```bash
changeguard propose --file examples/change_requests/allow_add_nullable_column.yml
changeguard runs
```

## Unexpected Decisions

### Expected BLOCK but got ALLOW

Usually means contract or lineage checks did not run:

- Table not registered in the workspace
- Wrong working directory (no `.changeguard/` nearby)
- Metadata files missing or pointing to the wrong table

Register the table and rerun `propose` from the workspace root.

### Expected ALLOW but got WARN or BLOCK

Review the `Checks`, `Reasons`, and `Impacted Assets` sections in the output. ChangeGuard aggregates individual check results:

```text
Any FAIL  → BLOCK
Any WARN  → WARN (if no FAIL)
All PASS  → ALLOW
```

See [decision_rules.md](decision_rules.md) for the rule matrix.

## Installation

### `changeguard: command not found`

Install the package in your environment:

```bash
pip install -e ".[dev]"
```

Or use the project virtualenv:

```bash
source .venv/bin/activate
changeguard --help
```

Or run through uv:

```bash
uv run changeguard --help
```

## Demo Script

### `./examples/demo_workflow.sh` fails immediately

Ensure the script is executable and run it from the repository root:

```bash
chmod +x examples/demo_workflow.sh
./examples/demo_workflow.sh
```

The script creates a temporary workspace and cleans it up on exit.

## Known Limitations

ChangeGuard does not apply database changes, parse full SQL migrations, or sync metadata from a remote catalog. See [limitations.md](limitations.md) for the full list.

## Related Docs

- [README quickstart](../README.md)
- [System design](system_design.md)
- [Limitations](limitations.md)
