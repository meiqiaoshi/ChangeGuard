"""End-to-end tests for the optional explanation layer."""

from pathlib import Path

from typer.testing import CliRunner

from changeguard.audit import load_run
from changeguard.cli import app
from changeguard.explain import explain_review
from changeguard.llm import NoOpLLMClient, OpenAICompatibleClient
from changeguard.registry import register_table
from changeguard.workspace import init_workspace, runs_path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def test_phase9_end_to_end_explanation_workflow(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    runner = CliRunner()

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0

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
            "--lineage",
            str(EXAMPLES_DIR / "lineage" / "sample_lineage.yml"),
        ],
    )
    assert register_result.exit_code == 0

    propose_result = runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "block_rename_required_column.yml")],
    )
    assert propose_result.exit_code == 0
    assert "Decision\nBLOCK" in propose_result.stdout

    review = load_run(project, "000001")
    noop_client = NoOpLLMClient()
    placeholder_client = OpenAICompatibleClient(api_key=None)

    explain_result = runner.invoke(app, ["explain-run", "000001"])
    assert explain_result.exit_code == 0
    expected = noop_client.explain_review(review)
    assert explain_result.stdout.strip() == expected.strip()
    assert explain_result.stdout.strip() == placeholder_client.explain_review(review).strip()
    assert explain_result.stdout.strip() == explain_review(review).strip()
    assert "BLOCK decision" in explain_result.stdout
    assert "failed one or more safety checks" in explain_result.stdout
    assert "mart_daily_revenue.total_amount" in explain_result.stdout
    assert "Add new column as nullable" in explain_result.stdout

    assert (runs_path(project) / "000001.json").is_file()
    assert review.decision.value == "BLOCK"


def test_phase9_explain_run_does_not_change_saved_review(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    init_workspace(project)
    register_table(
        project,
        name="sales",
        schema_path=str(EXAMPLES_DIR / "schemas" / "sales_schema.json"),
        contract_path=str(EXAMPLES_DIR / "contracts" / "sales_contract.yml"),
    )

    runner = CliRunner()
    runner.invoke(
        app,
        ["propose", "--file", str(EXAMPLES_DIR / "change_requests" / "allow_add_nullable_column.yml")],
    )

    before = load_run(project, "000001")
    runner.invoke(app, ["explain-run", "000001"])
    after = load_run(project, "000001")

    assert before == after
    assert before.decision.value == "ALLOW"
