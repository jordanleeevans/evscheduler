from datetime import datetime
from ariadne import MutationType

from app.repositories import VehicleRepository, ChargingSessionRepository

mutation = MutationType()


@mutation.field("createVehicle")
async def resolve_create_vehicle(
    obj, info, name: str, battery_capacity_kwh: float, current_battery_pct: float
):
    repo = VehicleRepository(info.context["db"])
    return await repo.create(
        name=name,
        battery_capacity_kwh=battery_capacity_kwh,
        current_battery_pct=current_battery_pct,
    )


@mutation.field("scheduleChargingSession")
async def resolve_schedule_charging_session(
    obj, info, vehicle_id: str, departure_time: str, target_charge_pct: float
):
    """Create a charging session and dispatch Celery task.
    TODO: Dispatch schedule_charging_session.delay(session.id).
    TODO: Validate vehicle exists and departure_time is in the future.
    """
    repo = ChargingSessionRepository(info.context["db"])
    session = await repo.create(
        vehicle_id=int(vehicle_id),
        departure_time=datetime.fromisoformat(departure_time),
        target_charge_pct=target_charge_pct,
    )
    # TODO: from app.tasks.scheduler import schedule_charging_session
    # TODO: schedule_charging_session.delay(session.id)
    return session


@mutation.field("cancelChargingSession")
async def resolve_cancel_charging_session(obj, info, id: str):
    """Cancel a charging session. TODO: Raise error if not found."""
    repo = ChargingSessionRepository(info.context["db"])
    return await repo.cancel(int(id))


@mutation.field("updateBatteryLevel")
async def resolve_update_battery_level(
    obj, info, vehicle_id: str, current_battery_pct: float
):
    """Update vehicle battery level. TODO: Raise error if not found."""
    repo = VehicleRepository(info.context["db"])
    return await repo.update_battery_level(int(vehicle_id), current_battery_pct)
