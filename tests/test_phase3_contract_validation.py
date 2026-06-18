"""End-to-end tests for contract validation workflows."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.changes import (
    load_change_request,
    validate_add_column,
    validate_drop_column,
    validate_rename_column,
)
from changeguard.cli import app
from changeguard.contracts import (
    check_add_column_against_contract,
    check_drop_column_against_contract,
    check_rename_column_against_contract,
    load_contract,
)
from changeguard.models import ChangeRequest, ChangeType, CheckStatus
from changeguard.registry import get_table
from changeguard.workspace import init_workspace, registry_path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _load_sales_contract(project: Path):
    table = get_table(project, "sales")
    contract_file = Path(table.contract_path)
    if not contract_file.is_absolute():
        contract_file = project / contract_file
    return load_contract(contract_file)


def test_phase3_end_to_end_contract_validation(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    runner = CliRunner()

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0
    assert registry_path(project).is_file()

    register_result = runner.invoke(
        app,
        [
            "register-table",
            "--name",
            "sales",
            "--schema",
            str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
            "--contract",
            str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
        ],
    )
    assert register_result.exit_code == 0

    check_contract_result = runner.invoke(app, ["check-contract", "sales"])
    assert check_contract_result.exit_code == 0
    assert "table: sales" in check_contract_result.stdout

    contract = _load_sales_contract(project)

    add_request = validate_add_column(
        ChangeRequest(
            change_type=ChangeType.ADD_COLUMN,
            table="sales",
            column="discount",
            column_type="float",
            nullable=True,
        )
    )
    add_results = check_add_column_against_contract(contract, add_request)
    assert add_results[0].status == CheckStatus.PASS

    add_yaml_request = validate_add_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "add_discount_column.yml")
    )
    add_yaml_results = check_add_column_against_contract(contract, add_yaml_request)
    assert add_yaml_results[0].status == CheckStatus.PASS

    rename_request = validate_rename_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")
    )
    rename_results = check_rename_column_against_contract(contract, rename_request)
    assert rename_results[0].status == CheckStatus.FAIL
    assert "required by contract" in rename_results[0].message

    drop_request = validate_drop_column(
        load_change_request(EXAMPLES_DIR / "change_requests" / "drop_customer_id.yml")
    )
    drop_results = check_drop_column_against_contract(contract, drop_request)
    assert drop_results[0].status == CheckStatus.FAIL
    assert "required by contract" in drop_results[0].message
