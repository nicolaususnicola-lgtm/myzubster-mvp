"""Economic provenance primitives for the MyZubster MVP.

This module records economic/asset facts without making legal ownership
determinations. Business rights and revenue splits must come from explicit
configuration or agreements outside the AI layer.
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Participant:
    participant_id: str
    display_name: str


@dataclass(frozen=True)
class Allocation:
    participant_id: str
    percentage: float


@dataclass(frozen=True)
class RevenueEvent:
    event_id: str
    source: str
    amount: float
    currency: str
    allocations: tuple[Allocation, ...]
    status: str = "RECORDED"

    def to_dict(self):
        return {
            "event_type": "REVENUE",
            **asdict(self),
            "allocations": [asdict(item) for item in self.allocations],
        }


@dataclass(frozen=True)
class AssetCreatedEvent:
    event_id: str
    asset_id: str
    asset_type: str
    creator_id: str
    provenance_status: str = "RECORDED"

    def to_dict(self):
        return {
            "event_type": "ASSET_CREATED",
            **asdict(self),
        }


def validate_allocations(allocations: tuple[Allocation, ...]) -> None:
    if not allocations:
        raise ValueError("Almeno una allocation è obbligatoria")

    total = sum(item.percentage for item in allocations)
    if total > 100:
        raise ValueError("La somma delle allocation non può superare il 100%")

    for item in allocations:
        if not item.participant_id.strip():
            raise ValueError("participant_id obbligatorio")
        if not 0 <= item.percentage <= 100:
            raise ValueError("Le percentuali devono essere tra 0 e 100")


def calculate_allocations(
    amount: float,
    allocations: tuple[Allocation, ...],
) -> dict[str, float]:
    if amount < 0:
        raise ValueError("L'importo non può essere negativo")

    validate_allocations(allocations)
    return {
        item.participant_id: round(amount * item.percentage / 100, 2)
        for item in allocations
    }


def create_nicola_nft_event(
    event_id: str,
    asset_id: str,
) -> AssetCreatedEvent:
    """Record an NFT created by Nicola as a provenance event.

    This records creator attribution supplied by the caller; it does not
    determine legal ownership or commercial value.
    """
    return AssetCreatedEvent(
        event_id=event_id,
        asset_id=asset_id,
        asset_type="NFT",
        creator_id="nicola",
    )



def calculate_balances(events: list[dict]) -> dict[str, dict[str, float]]:
    """Aggregate recorded revenue allocations by participant and currency."""
    balances: dict[str, dict[str, float]] = {}
    for event in events:
        if event.get("event_type") != "REVENUE":
            continue
        currency = str(event.get("currency", "")).strip()
        if not currency:
            continue
        for participant_id, amount in (event.get("calculated_amounts") or {}).items():
            participant = balances.setdefault(
                str(participant_id),
                {},
            )
            participant[currency] = round(
                participant.get(currency, 0.0) + float(amount),
                2,
            )
    return balances
