import logging
from ariadne import QueryType, ObjectType, ScalarType
from sqlalchemy import select
from app.models import Vehicle, ChargingSession
from app.services.tariff_service import create_half_hourly_tariffs
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

query = QueryType()
vehicle_type = ObjectType("Vehicle")
charging_session_type = ObjectType("ChargingSession")
charging_slot_type = ObjectType("ChargingSlot")
datetime_scalar = ScalarType("DateTime")

@datetime_scalar.serializer
def serialize_datetime(value):
    return value.isoformat()

@query.field("vehicles")
async def resolve_vehicles(obj, info):
    """Return all vehicles from the database. TODO: Add pagination."""
    db = info.context["db"]
    result = await db.execute(select(Vehicle))
    return result.scalars().all()


@query.field("vehicle")
async def resolve_vehicle(obj, info, id):
    """Return a single vehicle by ID. TODO: Raise GraphQL error if not found."""
    db = info.context["db"]
    result = await db.execute(select(Vehicle).where(Vehicle.id == int(id)))
    return result.scalar_one_or_none()


@query.field("chargingSessions")
async def resolve_charging_sessions(obj, info):
    """Return all charging sessions. TODO: Add filtering by status and vehicle."""
    db = info.context["db"]
    result = await db.execute(select(ChargingSession))
    return result.scalars().all()


@query.field("chargingSession")
async def resolve_charging_session(obj, info, id):
    """Return a single charging session by ID. TODO: Raise GraphQL error if not found."""
    db = info.context["db"]
    result = await db.execute(select(ChargingSession).where(ChargingSession.id == int(id)))
    return result.scalar_one_or_none()


@query.field("tariffPrices")
async def resolve_tariff_prices(obj, info, **kwargs):
    """Return mock tariff prices for the given time window. TODO: Replace mock with live API."""
    from_str = kwargs.get("from")
    to_str = kwargs.get("to")
    region = kwargs.get("region", "C")

    from_dt = datetime.fromisoformat(from_str)
    to_dt = datetime.fromisoformat(to_str)

    logger.info(f"Fetching tariff prices for region {region} from {from_dt} to {to_dt}")

    prices = create_half_hourly_tariffs(from_dt, to_dt, region)

    logger.info(f"Returning {len(prices)} tariff price entries")

    return [
        {
            "slot_start": p.slot_start,
            "slot_end": p.slot_end,
            "price_per_kwh": p.price_per_kwh,
        }
        for p in prices
    ]
