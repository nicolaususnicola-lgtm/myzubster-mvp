from src.core.economics import (
    Allocation,
    AssetCreatedEvent,
    RevenueEvent,
    calculate_allocations,
    create_nicola_nft_event,
    validate_allocations,
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
    }
