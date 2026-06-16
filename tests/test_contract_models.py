"""Tests for data contract models."""

from changeguard.models import Contract, ContractColumn, ContractRule


def test_contract_column_model() -> None:
    column = ContractColumn(
        type="float",
        required=True,
        min_value=0,
    )

    assert column.type == "float"
    assert column.required is True
    assert column.min_value == 0


def test_contract_rule_model() -> None:
    rule = ContractRule(
        name="amount_non_negative",
        column="amount",
        check="min_value",
        value=0,
    )

    assert rule.name == "amount_non_negative"
    assert rule.column == "amount"
    assert rule.check == "min_value"


def test_contract_model_in_memory() -> None:
    contract = Contract(
        table="sales",
        version="1.0",
        owner="analytics-team",
        description="Core sales fact table contract",
        columns={
            "order_id": ContractColumn(
                type="string",
                required=True,
                unique=True,
                primary_key=True,
            ),
            "amount": ContractColumn(
                type="float",
                required=True,
                min_value=0,
            ),
            "status": ContractColumn(
                type="string",
                required=False,
            ),
        },
        rules=[
            ContractRule(
                name="amount_non_negative",
                column="amount",
                check="min_value",
                value=0,
            )
        ],
    )

    assert contract.table == "sales"
    assert contract.version == "1.0"
    assert contract.owner == "analytics-team"
    assert contract.columns["amount"].required is True
    assert contract.rules[0].name == "amount_non_negative"


def test_contract_model_serialization_round_trip() -> None:
    contract = Contract(
        table="sales",
        version="1.0",
        columns={
            "customer_id": ContractColumn(type="string", required=True),
        },
    )

    payload = contract.model_dump(mode="json")
    restored = Contract.model_validate(payload)

    assert restored == contract
