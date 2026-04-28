import logging
from ariadne import QueryType, ObjectType, ScalarType
from ..models import Vehicle, ChargingSession
from ..services.tariff_service import create_half_hourly_tariffs
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
def resolve_vehicles(obj, info):
    """Return all vehicles from the database. TODO: Add pagination."""
    db = info.context["db"]
    return db.query(Vehicle).all()


@query.field("vehicle")
def resolve_vehicle(obj, info, id):
    """Return a single vehicle by ID. TODO: Raise GraphQL error if not found."""
    db = info.context["db"]
    return db.query(Vehicle).filter(Vehicle.id == int(id)).first()


@query.field("chargingSessions")
def resolve_charging_sessions(obj, info):
    """Return all charging sessions. TODO: Add filtering by status and vehicle."""
    db = info.context["db"]
    return db.query(ChargingSession).all()


@query.field("chargingSession")
def resolve_charging_session(obj, info, id):
    """Return a single charging session by ID. TODO: Raise GraphQL error if not found."""
    db = info.context["db"]
    return db.query(ChargingSession).filter(ChargingSession.id == int(id)).first()


@query.field("tariffPrices")
def resolve_tariff_prices(obj, info, **kwargs):
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
