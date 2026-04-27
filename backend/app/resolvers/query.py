from ariadne import QueryType, ObjectType
from ..models import Vehicle, ChargingSession
from ..services.tariff_service import get_mock_prices
from datetime import datetime

query = QueryType()
vehicle_type = ObjectType("Vehicle")
charging_session_type = ObjectType("ChargingSession")
charging_slot_type = ObjectType("ChargingSlot")

# Vehicle field resolvers (snake_case -> camelCase)
vehicle_type.set_field("batteryCapacityKwh", lambda obj, info: obj.battery_capacity_kwh)
vehicle_type.set_field("currentBatteryPct", lambda obj, info: obj.current_battery_pct)
vehicle_type.set_field("createdAt", lambda obj, info: obj.created_at.isoformat() if obj.created_at else None)

# ChargingSession field resolvers
charging_session_type.set_field("departureTime", lambda obj, info: obj.departure_time.isoformat() if obj.departure_time else None)
charging_session_type.set_field("targetChargePct", lambda obj, info: obj.target_charge_pct)
charging_session_type.set_field("createdAt", lambda obj, info: obj.created_at.isoformat() if obj.created_at else None)
charging_session_type.set_field("status", lambda obj, info: obj.status.upper())
charging_session_type.set_field("slots", lambda obj, info: obj.slots if obj.slots else [])

# ChargingSlot field resolvers
charging_slot_type.set_field("slotStart", lambda obj, info: obj.slot_start.isoformat() if obj.slot_start else None)
charging_slot_type.set_field("slotEnd", lambda obj, info: obj.slot_end.isoformat() if obj.slot_end else None)
charging_slot_type.set_field("pricePerKwh", lambda obj, info: obj.price_per_kwh)
charging_slot_type.set_field("isSelected", lambda obj, info: obj.is_selected)


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

    prices = get_mock_prices(from_dt, to_dt, region)
    return [
        {
            "slotStart": p.slot_start.isoformat(),
            "slotEnd": p.slot_end.isoformat(),
            "pricePerKwh": p.price_per_kwh,
        }
        for p in prices
    ]
