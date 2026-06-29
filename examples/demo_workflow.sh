#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
EXAMPLES_DIR="${SCRIPT_DIR}"

if command -v changeguard >/dev/null 2>&1; then
  CHANGEGUARD=(changeguard)
elif [[ -x "${REPO_ROOT}/.venv/bin/changeguard" ]]; then
  CHANGEGUARD=("${REPO_ROOT}/.venv/bin/changeguard")
else
  CHANGEGUARD=(uv run --directory "${REPO_ROOT}" changeguard)
fi

DEMO_DIR="$(mktemp -d "${TMPDIR:-/tmp}/changeguard-demo.XXXXXX")"
cleanup() {
  rm -rf "${DEMO_DIR}"
}
trap cleanup EXIT

cd "${DEMO_DIR}"

echo "==> Demo workspace: ${DEMO_DIR}"
echo

echo "==> Initialize workspace"
"${CHANGEGUARD[@]}" init
echo

echo "==> Register sales table"
"${CHANGEGUARD[@]}" register-table \
  --name sales \
  --schema "${EXAMPLES_DIR}/schemas/sales_schema.json" \
  --contract "${EXAMPLES_DIR}/contracts/sales_contract.yml" \
  --lineage "${EXAMPLES_DIR}/lineage/sample_lineage.yml"
echo

echo "==> List registered tables"
"${CHANGEGUARD[@]}" tables
echo

echo "==> Inspect sales metadata"
"${CHANGEGUARD[@]}" inspect sales
echo

echo "==> Show downstream impact for sales.amount"
"${CHANGEGUARD[@]}" impact sales.amount
echo

echo "==> Propose allowed change"
"${CHANGEGUARD[@]}" propose \
  --file "${EXAMPLES_DIR}/change_requests/allow_add_nullable_column.yml"
echo

echo "==> Propose blocked change"
"${CHANGEGUARD[@]}" propose \
  --file "${EXAMPLES_DIR}/change_requests/block_rename_required_column.yml"
echo

echo "==> List saved review runs"
"${CHANGEGUARD[@]}" runs
echo

echo "==> Review saved run 000001"
"${CHANGEGUARD[@]}" review-run 000001
echo

echo "Demo workflow completed successfully."
