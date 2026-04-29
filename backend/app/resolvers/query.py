import logging
from ariadne import QueryType, ObjectType
from app.repositories import VehicleRepository, ChargingSessionRepository
from app.services.tariff_service import create_half_hourly_tariffs

logger = logging.getLogger(__name__)

query = QueryType()
vehicle_type = ObjectType("Vehicle")
charging_session_type = ObjectType("ChargingSession")
charging_slot_type = ObjectType("ChargingSlot")


@query.field("vehicles")
async def resolve_vehicles(obj, info):
    repo = VehicleRepository(info.context["db"])
    return await repo.get_all()


@query.field("vehicle")
async def resolve_vehicle(obj, info, id):
    repo = VehicleRepository(info.context["db"])
    return await repo.get_by_id(int(id))


@query.field("chargingSessions")
async def resolve_charging_sessions(obj, info):
    repo = ChargingSessionRepository(info.context["db"])
    return await repo.get_all()


@query.field("chargingSession")
async def resolve_charging_session(obj, info, id):
    repo = ChargingSessionRepository(info.context["db"])
    return await repo.get_by_id(int(id))


@query.field("tariffPrices")
async def resolve_tariff_prices(obj, info, **kwargs):
    """Return mock tariff prices for the given time window. TODO: Replace mock with live API."""
    from_dt = kwargs.get("from")  # datetime (parsed by DateTime scalar)
    to_dt = kwargs.get("to")  # datetime (parsed by DateTime scalar)
    region = kwargs.get("region", "C")

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
