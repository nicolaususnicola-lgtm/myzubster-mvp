from src.core.economics import (
    Allocation,
    AssetCreatedEvent,
    RevenueEvent,
    calculate_allocations,
    create_nicola_nft_event,
    validate_allocations,
    calculate_balances,
    calculate_balance_breakdown,
    normalize_revenue_source,
)


def test_revenue_allocations_are_calculated_from_explicit_rules():
    allocations = (
        Allocation(participant_id="daniel", percentage=2),
        Allocation(participant_id="nicola", percentage=98),
    )

    assert calculate_allocations(1000, allocations) == {
        "daniel": 20.0,
        "nicola": 980.0,
    }


def test_allocation_rules_cannot_exceed_total_revenue():
    allocations = (
        Allocation(participant_id="daniel", percentage=60),
        Allocation(participant_id="nicola", percentage=50),
    )

    try:
        validate_allocations(allocations)
    except ValueError as error:
        assert "100%" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_revenue_event_serializes_auditable_source_and_allocations():
    event = RevenueEvent(
        event_id="rev-001",
        source="MYZUBSTER_ONLINE",
        amount=1000,
        currency="EUR",
        allocations=(Allocation("daniel", 2),),
    )

    assert event.to_dict() == {
        "event_type": "REVENUE",
        "event_id": "rev-001",
        "source": "MYZUBSTER_ONLINE",
        "amount": 1000,
        "currency": "EUR",
        "allocations": [{"participant_id": "daniel", "percentage": 2}],
        "status": "RECORDED",
        "created_at": event.to_dict()["created_at"],
    }


def test_nicola_nft_is_recorded_as_creator_provenance():
    event = create_nicola_nft_event("asset-001", "n4k48-comic-001")

    assert isinstance(event, AssetCreatedEvent)
    assert event.to_dict() == {
        "event_type": "ASSET_CREATED",
        "event_id": "asset-001",
        "asset_id": "n4k48-comic-001",
        "asset_type": "NFT",
        "creator_id": "nicola",
        "provenance_status": "RECORDED",
        "created_at": event.to_dict()["created_at"],
    }



def test_balances_are_derived_from_recorded_revenue_events():
    events = [
        {
            "event_type": "REVENUE",
            "currency": "EUR",
            "calculated_amounts": {"daniel": 20.0, "nicola": 980.0},
        },
        {
            "event_type": "REVENUE",
            "currency": "EUR",
            "calculated_amounts": {"daniel": 10.0, "nicola": 490.0},
        },
        {
            "event_type": "ASSET_CREATED",
            "creator_id": "nicola",
        },
    ]

    assert calculate_balances(events) == {
        "daniel": {"EUR": 30.0},
        "nicola": {"EUR": 1470.0},
    }



def test_revenue_source_is_explicit_and_normalized():
    assert normalize_revenue_source("zorgax") == "ZORGAX"


def test_unknown_revenue_source_is_rejected():
    try:
        normalize_revenue_source("OTHER")
    except ValueError as error:
        assert "source non valida" in str(error)
    else:
        raise AssertionError("Expected unsupported source to be rejected")


def test_balance_breakdown_groups_amounts_by_source():
    events = [
        {
            "event_type": "REVENUE",
            "source": "MYZUBSTER_ONLINE",
            "currency": "EUR",
            "calculated_amounts": {"daniel": 20.0, "nicola": 980.0},
        },
        {
            "event_type": "REVENUE",
            "source": "ZORGAX",
            "currency": "EUR",
            "calculated_amounts": {"nicola": 50.0},
        },
    ]

    assert calculate_balance_breakdown(events) == {
        "daniel": {
            "balances": {"EUR": 20.0},
            "by_source": {"MYZUBSTER_ONLINE": {"EUR": 20.0}},
        },
        "nicola": {
            "balances": {"EUR": 1030.0},
            "by_source": {
                "MYZUBSTER_ONLINE": {"EUR": 980.0},
                "ZORGAX": {"EUR": 50.0},
            },
        },
    }



def test_revenue_event_accepts_explicit_audit_timestamp():
    event = RevenueEvent(
        event_id="rev-time-001",
        source="ZORGAX",
        amount=10,
        currency="EUR",
        allocations=(Allocation("nicola", 100),),
        created_at="2026-09-18T20:00:00.000Z",
    )

    assert event.to_dict()["created_at"] == "2026-09-18T20:00:00.000Z"


def test_asset_event_accepts_explicit_audit_timestamp():
    event = AssetCreatedEvent(
        event_id="asset-time-001",
        asset_id="asset-001",
        asset_type="NFT",
        creator_id="nicola",
        created_at="2026-09-18T20:00:00.000Z",
    )

    assert event.to_dict()["created_at"] == "2026-09-18T20:00:00.000Z"
def test_revenue_simulator_calculates_costs_and_margin():
    from src.core.economics import simulate_revenue

    result = simulate_revenue(
        transactions=500,
        average_ticket=100,
        zorgax_pro_users=30,
        zorgax_developer_users=5,
        marketplace_commission_percent=2.0,
        payment_fee_percent=1.5,
        payment_fee_fixed=0.25,
        ai_monthly_cost=100,
        hosting_monthly_cost=50,
        other_monthly_cost=25,
    )

    assert result["gmv"] == 50000.0
    assert result["marketplace"]["revenue"] == 1000.0

    assert result["zorgax"]["pro"]["revenue"] == 297.0
    assert result["zorgax"]["developer"]["revenue"] == 149.5

    assert result["monthly_revenue"] == 1446.5

    assert result["costs"]["payment_percentage_cost"] == 750.0
    assert result["costs"]["payment_fixed_cost"] == 125.0
    assert result["costs"]["payment_cost"] == 875.0

    assert result["monthly_costs"] == 1050.0
    assert result["monthly_margin"] == 396.5

    assert result["annualized_revenue"] == 17358.0
    assert result["annualized_costs"] == 12600.0
    assert result["annualized_margin"] == 4758.0
def test_revenue_simulator_calculates_revenue():
    from src.core.economics import simulate_revenue

    result = simulate_revenue(
        transactions=500,
        average_ticket=100,
        zorgax_pro_users=30,
        zorgax_developer_users=5,
    )

    assert result["scenario"] is True
    assert result["currency"] == "EUR"
    assert result["gmv"] == 50000.0
    assert result["marketplace"]["commission_percent"] == 2.0
    assert result["marketplace"]["revenue"] == 1000.0
    assert result["zorgax"]["pro"]["revenue"] == 297.0
    assert result["zorgax"]["developer"]["revenue"] == 149.5
    assert result["monthly_revenue"] == 1446.5
    assert result["annualized_revenue"] == 17358.0


def test_revenue_simulator_rejects_negative_values():
    import pytest

    from src.core.economics import simulate_revenue

    with pytest.raises(ValueError):
        simulate_revenue(
            transactions=-1,
            average_ticket=100,
        )


def test_revenue_simulator_api():
    from src.api.server import app

    client = app.test_client()

    response = client.post(
        "/api/economics/simulate",
        json={
            "transactions": 500,
            "average_ticket": 100,
            "zorgax_pro_users": 30,
            "zorgax_developer_users": 5,
        },
    )

    assert response.status_code == 200

    result = response.get_json()

    assert result["scenario"] is True
    assert result["gmv"] == 50000.0
    assert result["marketplace"]["revenue"] == 1000.0
    assert result["zorgax"]["pro"]["revenue"] == 297.0
    assert result["zorgax"]["developer"]["revenue"] == 149.5
    assert result["monthly_revenue"] == 1446.5
    assert result["annualized_revenue"] == 17358.0


def test_revenue_simulator_api_rejects_negative_values():
    from src.api.server import app

    client = app.test_client()

    response = client.post(
        "/api/economics/simulate",
        json={
            "transactions": -1,
            "average_ticket": 100,
        },
    )

    assert response.status_code == 400