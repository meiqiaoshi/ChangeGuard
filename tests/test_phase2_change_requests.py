"""End-to-end tests for change request workflows."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.changes import build_change_request, load_change_request, validate_add_column
from changeguard.cli import app
from changeguard.models import ChangeType
from changeguard.registry import get_table, load_registry
from changeguard.render import render_change_request
from changeguard.workspace import init_workspace, registry_path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def test_phase2_end_to_end_change_request_flow(tmp_path: Path, monkeypatch) -> None:
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

    registry = load_registry(project)
    assert len(registry.tables) == 1
    assert get_table(project, "sales").name == "sales"

    yaml_request = load_change_request(
        EXAMPLES_DIR / "change_requests" / "add_discount_column.yml"
    )
    validated_yaml_request = validate_add_column(yaml_request)
    yaml_output = render_change_request(validated_yaml_request)
    assert "change_type: add_column" in yaml_output
    assert "column: discount" in yaml_output

    yaml_propose_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "rename_amount_column.yml")],
    )
    assert yaml_propose_result.exit_code == 0
    assert "change_type: rename_column" in yaml_propose_result.stdout
    assert "new_name: order_amount" in yaml_propose_result.stdout

    flag_propose_result = runner.invoke(
        app,
        [
            "propose",
            "--change-type",
            "add_column",
            "--table",
            "sales",
            "--column",
            "discount",
            "--type",
            "float",
            "--nullable",
            "true",
        ],
    )
    assert flag_propose_result.exit_code == 0
    assert "change_type: add_column" in flag_propose_result.stdout
    assert "nullable: true" in flag_propose_result.stdout

    flag_request = build_change_request(
        change_type=ChangeType.RENAME_COLUMN,
        table="sales",
        column="amount",
        new_name="order_amount",
    )
    rendered_flag_request = render_change_request(flag_request)
    assert "change_type: rename_column" in rendered_flag_request
    assert "new_name: order_amount" in rendered_flag_request
