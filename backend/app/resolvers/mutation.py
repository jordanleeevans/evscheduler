from datetime import datetime, timezone

from graphql import GraphQLError
from ariadne import MutationType

from app.repositories import VehicleRepository, ChargingSessionRepository

mutation = MutationType()


@mutation.field("createVehicle")
async def resolve_create_vehicle(
    obj, info, name: str, battery_capacity_kwh: float, current_battery_pct: float
):
    if battery_capacity_kwh <= 0:
        raise GraphQLError("batteryCapacityKwh must be greater than 0.")
    repo = VehicleRepository(info.context["db"])
    return await repo.create(
        name=name,
        battery_capacity_kwh=battery_capacity_kwh,
        current_battery_pct=current_battery_pct,
    )


@mutation.field("scheduleChargingSession")
async def resolve_schedule_charging_session(
    obj, info, vehicle_id: str, departure_time: datetime, target_charge_pct: float
):
    db = info.context["db"]

    vehicle = await VehicleRepository(db).get_by_id(int(vehicle_id))
    if vehicle is None:
        raise GraphQLError(f"Vehicle with id {vehicle_id} not found.")

    if departure_time <= datetime.now(timezone.utc):
        raise GraphQLError("departureTime must be in the future.")

    session = await ChargingSessionRepository(db).create(
        vehicle_id=int(vehicle_id),
        departure_time=departure_time,
        target_charge_pct=target_charge_pct,
    )
    # TODO: from app.tasks.scheduler import schedule_charging_session
    # TODO: schedule_charging_session.delay(session.id)
    return session


@mutation.field("cancelChargingSession")
async def resolve_cancel_charging_session(obj, info, id: str):
    repo = ChargingSessionRepository(info.context["db"])
    session = await repo.cancel(int(id))
    if session is None:
        raise GraphQLError(f"Charging session with id {id} not found.")
    return session


@mutation.field("updateBatteryLevel")
async def resolve_update_battery_level(
    obj, info, vehicle_id: str, current_battery_pct: float
):
    repo = VehicleRepository(info.context["db"])
    vehicle = await repo.update_battery_level(int(vehicle_id), current_battery_pct)
    if vehicle is None:
        raise GraphQLError(f"Vehicle with id {vehicle_id} not found.")
    return vehicle
