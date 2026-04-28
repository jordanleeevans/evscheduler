from datetime import datetime, timezone
from ariadne import MutationType

from app.models import Vehicle, ChargingSession
from app.models.charging_session import SessionStatus

mutation = MutationType()


@mutation.field("createVehicle")
def resolve_create_vehicle(obj, info, name: str, battery_capacity_kwh: float, current_battery_pct: float):
    """Create a new vehicle. TODO: Validate inputs."""
    db = info.context["db"]
    vehicle = Vehicle(
        name=name,
        battery_capacity_kwh=battery_capacity_kwh,
        current_battery_pct=current_battery_pct,
        created_at=datetime.now(timezone.utc),
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@mutation.field("scheduleChargingSession")
def resolve_schedule_charging_session(obj, info, vehicle_id: str, departure_time: str, target_charge_pct: float):
    """Create a charging session and dispatch Celery task.
    TODO: Dispatch schedule_charging_session.delay(session.id).
    TODO: Validate vehicle exists and departure_time is in the future.
    """
    db = info.context["db"]
    session = ChargingSession(
        vehicle_id=int(vehicle_id),
        departure_time=datetime.fromisoformat(departure_time),
        target_charge_pct=target_charge_pct,
        status=SessionStatus.PENDING.value,
        created_at=datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    # TODO: from ..tasks.scheduler import schedule_charging_session
    # TODO: schedule_charging_session.delay(session.id)
    return session


@mutation.field("cancelChargingSession")
def resolve_cancel_charging_session(obj, info, id: str):
    """Cancel a charging session. TODO: Raise error if not found or already completed."""
    db = info.context["db"]
    session = db.query(ChargingSession).filter(ChargingSession.id == int(id)).first()
    if session:
        session.status = "cancelled"
        db.commit()
        db.refresh(session)
    # TODO: raise error if not found
    return session


@mutation.field("updateBatteryLevel")
def resolve_update_battery_level(obj, info, vehicle_id: str, current_battery_pct: float):
    """Update vehicle battery level. TODO: Raise error if not found."""
    db = info.context["db"]
    vehicle = db.query(Vehicle).filter(Vehicle.id == int(vehicle_id)).first()
    if vehicle:
        vehicle.current_battery_pct = current_battery_pct
        db.commit()
        db.refresh(vehicle)
    # TODO: raise error if not found
    return vehicle
