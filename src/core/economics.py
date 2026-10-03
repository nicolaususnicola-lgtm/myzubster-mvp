"""Economic provenance primitives for the MyZubster MVP.

This module records economic/asset facts without making legal ownership
determinations. Business rights and revenue splits must come from explicit
configuration or agreements outside the AI layer.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Return an audit timestamp in UTC using ISO 8601 with a Z suffix."""
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


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
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self):
        return {
            "event_type": "REVENUE",
            **asdict(self),
            "created_at": self.created_at,
            "allocations": [
                asdict(item)
                for item in self.allocations
            ],
        }


@dataclass(frozen=True)
class AssetCreatedEvent:
    event_id: str
    asset_id: str
    asset_type: str
    creator_id: str
    provenance_status: str = "RECORDED"
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self):
        return {
            "event_type": "ASSET_CREATED",
            **asdict(self),
            "created_at": self.created_at,
        }


def validate_allocations(
    allocations: tuple[Allocation, ...],
) -> None:
    if not allocations:
        raise ValueError(
            "Almeno una allocation è obbligatoria"
        )

    total = sum(
        item.percentage
        for item in allocations
    )

    if total > 100:
        raise ValueError(
            "La somma delle allocation non può superare il 100%"
        )

    for item in allocations:
        if not item.participant_id.strip():
            raise ValueError(
                "participant_id obbligatorio"
            )

        if not 0 <= item.percentage <= 100:
            raise ValueError(
                "Le percentuali devono essere tra 0 e 100"
            )


def calculate_allocations(
    amount: float,
    allocations: tuple[Allocation, ...],
) -> dict[str, float]:
    if amount < 0:
        raise ValueError(
            "L'importo non può essere negativo"
        )

    validate_allocations(allocations)

    return {
        item.participant_id: round(
            amount * item.percentage / 100,
            2,
        )
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


def calculate_balances(
    events: list[dict],
) -> dict[str, dict[str, float]]:
    """Aggregate recorded revenue allocations by participant and currency."""

    balances: dict[str, dict[str, float]] = {}

    for event in events:
        if event.get("event_type") != "REVENUE":
            continue

        currency = str(
            event.get("currency", "")
        ).strip()

        if not currency:
            continue

        for participant_id, amount in (
            event.get("calculated_amounts") or {}
        ).items():
            participant = balances.setdefault(
                str(participant_id),
                {},
            )

            participant[currency] = round(
                participant.get(currency, 0.0)
                + float(amount),
                2,
            )

    return balances


REVENUE_SOURCES = (
    "MYZUBSTER_ONLINE",
    "CONVERSION",
    "ZORGAX",
    "NFT",
    "SOFTWARE",
    "KNOWLEDGE",
)


def normalize_revenue_source(
    source: str,
) -> str:
    """Validate and normalize an explicit revenue source identifier."""

    normalized = str(source).strip().upper()

    if normalized not in REVENUE_SOURCES:
        raise ValueError(
            "source non valida; usare una delle fonti supportate: "
            + ", ".join(REVENUE_SOURCES)
        )

    return normalized


def calculate_balance_breakdown(
    events: list[dict],
) -> dict[str, dict]:
    """Aggregate participant balances by currency and by explicit source."""

    result: dict[str, dict] = {}

    for event in events:
        if event.get("event_type") != "REVENUE":
            continue

        currency = str(
            event.get("currency", "")
        ).strip()

        source = str(
            event.get("source", "")
        ).strip()

        if not currency or not source:
            continue

        for participant_id, amount in (
            event.get("calculated_amounts") or {}
        ).items():
            participant = result.setdefault(
                str(participant_id),
                {
                    "balances": {},
                    "by_source": {},
                },
            )

            value = float(amount)

            participant["balances"][currency] = round(
                participant["balances"].get(
                    currency,
                    0.0,
                )
                + value,
                2,
            )

            source_totals = participant[
                "by_source"
            ].setdefault(
                source,
                {},
            )

            source_totals[currency] = round(
                source_totals.get(
                    currency,
                    0.0,
                )
                + value,
                2,
            )

    return result


def simulate_revenue(
    transactions: int,
    average_ticket: float,
    zorgax_pro_users: int = 0,
    zorgax_developer_users: int = 0,
    marketplace_commission_percent: float = 2.0,
    payment_fee_percent: float = 0.0,
    payment_fee_fixed: float = 0.0,
    ai_monthly_cost: float = 0.0,
    hosting_monthly_cost: float = 0.0,
    other_monthly_cost: float = 0.0,
) -> dict:
    """Simulate revenue, costs and margin without recording ledger events."""

    values = (
        transactions,
        average_ticket,
        zorgax_pro_users,
        zorgax_developer_users,
        marketplace_commission_percent,
        payment_fee_percent,
        payment_fee_fixed,
        ai_monthly_cost,
        hosting_monthly_cost,
        other_monthly_cost,
    )

    if any(value < 0 for value in values):
        raise ValueError(
            "simulation values must be non-negative"
        )

    zorgax_pro_price = 9.90
    zorgax_developer_price = 29.90

    gmv = round(
        transactions * average_ticket,
        2,
    )

    marketplace_revenue = round(
        gmv
        * (
            marketplace_commission_percent
            / 100
        ),
        2,
    )

    zorgax_pro_revenue = round(
        zorgax_pro_users
        * zorgax_pro_price,
        2,
    )

    zorgax_developer_revenue = round(
        zorgax_developer_users
        * zorgax_developer_price,
        2,
    )

    monthly_revenue = round(
        marketplace_revenue
        + zorgax_pro_revenue
        + zorgax_developer_revenue,
        2,
    )

    payment_percentage_cost = round(
        gmv
        * (
            payment_fee_percent
            / 100
        ),
        2,
    )

    payment_fixed_cost = round(
        transactions
        * payment_fee_fixed,
        2,
    )

    payment_cost = round(
        payment_percentage_cost
        + payment_fixed_cost,
        2,
    )

    monthly_costs = round(
        payment_cost
        + ai_monthly_cost
        + hosting_monthly_cost
        + other_monthly_cost,
        2,
    )

    monthly_margin = round(
        monthly_revenue
        - monthly_costs,
        2,
    )

    annualized_revenue = round(
        monthly_revenue * 12,
        2,
    )

    annualized_costs = round(
        monthly_costs * 12,
        2,
    )

    annualized_margin = round(
        monthly_margin * 12,
        2,
    )

    return {
        "scenario": True,
        "currency": "EUR",
        "transactions": transactions,
        "average_ticket": average_ticket,
        "gmv": gmv,
        "marketplace": {
            "commission_percent": marketplace_commission_percent,
            "revenue": marketplace_revenue,
        },
        "zorgax": {
            "pro": {
                "users": zorgax_pro_users,
                "price": zorgax_pro_price,
                "revenue": zorgax_pro_revenue,
            },
            "developer": {
                "users": zorgax_developer_users,
                "price": zorgax_developer_price,
                "revenue": zorgax_developer_revenue,
            },
        },
        "costs": {
            "payment_fee_percent": payment_fee_percent,
            "payment_fee_fixed": payment_fee_fixed,
            "payment_percentage_cost": payment_percentage_cost,
            "payment_fixed_cost": payment_fixed_cost,
            "payment_cost": payment_cost,
            "ai_monthly_cost": round(
                ai_monthly_cost,
                2,
            ),
            "hosting_monthly_cost": round(
                hosting_monthly_cost,
                2,
            ),
            "other_monthly_cost": round(
                other_monthly_cost,
                2,
            ),
            "monthly_costs": monthly_costs,
        },
        "monthly_revenue": monthly_revenue,
        "monthly_costs": monthly_costs,
        "monthly_margin": monthly_margin,
        "annualized_revenue": annualized_revenue,
        "annualized_costs": annualized_costs,
        "annualized_margin": annualized_margin,
        "disclaimer": (
            "Scenario only. Cost inputs are assumptions supplied "
            "to the simulator. Values are not recorded revenue, "
            "actual expenses, payments, wallet funds, profit, "
            "or financial forecasts."
        ),
    }