"""Tests for rendering structured review results."""

from changeguard.models import (
    CheckResult,
    CheckStatus,
    Decision,
    ReviewResult,
    RiskLevel,
)
from changeguard.render import render_review_result


def test_render_review_result_block_with_checks_and_impacts() -> None:
    result = ReviewResult(
        decision=Decision.BLOCK,
        risk_level=RiskLevel.HIGH,
        reasons=[
            "Column amount is required by contract for table sales",
            "Column amount is referenced by downstream assets: mart_daily_revenue.total_amount",
        ],
        check_results=[
            CheckResult(
                name="contract_rename_required_column",
                status=CheckStatus.FAIL,
                message="Column amount is required by contract for table sales",
            ),
            CheckResult(
                name="lineage_rename_column_in_use",
                status=CheckStatus.FAIL,
                message="Column amount is referenced by downstream assets: mart_daily_revenue.total_amount",
                source="lineage",
            ),
        ],
        impacted_assets=["mart_daily_revenue.total_amount", "sales_dashboard.revenue_kpi"],
    )

    output = render_review_result(result)

    assert output == (
        "Decision\n"
        "BLOCK\n"
        "\n"
        "Risk Level\n"
        "HIGH\n"
        "\n"
        "Checks\n"
        "- [FAIL] (contract) Column amount is required by contract for table sales\n"
        "- [FAIL] (lineage) Column amount is referenced by downstream assets: mart_daily_revenue.total_amount\n"
        "\n"
        "Impacted Assets\n"
        "- mart_daily_revenue.total_amount\n"
        "- sales_dashboard.revenue_kpi\n"
        "\n"
        "Reasons\n"
        "- Column amount is required by contract for table sales\n"
        "- Column amount is referenced by downstream assets: mart_daily_revenue.total_amount"
    )


def test_render_review_result_allow_with_no_reasons() -> None:
    result = ReviewResult(
        decision=Decision.ALLOW,
        risk_level=RiskLevel.LOW,
        check_results=[
            CheckResult(
                name="contract_add_nullable_column",
                status=CheckStatus.PASS,
                message="Adding nullable column discount is allowed by contract",
            )
        ],
    )

    output = render_review_result(result)

    assert "Decision\nALLOW" in output
    assert "Risk Level\nLOW" in output
    assert "Reasons\n(none)" in output
    assert "Impacted Assets\n(none)" in output
