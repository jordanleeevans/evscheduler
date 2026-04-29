"""Celery tasks for charging session scheduling."""

from app.celery_app import celery_app


@celery_app.task(name="tasks.schedule_charging_session")
def schedule_charging_session(session_id: int) -> dict:
    """Schedule charging slots for a session.

    Retrieves the session, calls find_cheapest_slots, creates ChargingSlot
    records and updates the session status to 'scheduled'.

    Args:
        session_id: The ID of the ChargingSession to schedule.

    Returns:
        Dict with session_id and slot count.

    TODO: Implement slot creation logic.
    TODO: Send OCPP mock command to start charger at first slot.
    """
    from app.database import SessionLocal
    from app.models import ChargingSession, Vehicle
    from app.services.scheduler_service import find_cheapest_slots

    db = SessionLocal()
    try:
        session = (
            db.query(ChargingSession).filter(ChargingSession.id == session_id).first()
        )
        if session is None:
            return {"error": f"Session {session_id} not found"}

        vehicle = db.query(Vehicle).filter(Vehicle.id == session.vehicle_id).first()
        if vehicle is None:
            return {"error": f"Vehicle {session.vehicle_id} not found"}

        # TODO: Call find_cheapest_slots and create ChargingSlot records
        slots = find_cheapest_slots(
            departure_time=session.departure_time,
            current_battery_pct=vehicle.current_battery_pct,
            target_charge_pct=session.target_charge_pct,
            battery_capacity_kwh=vehicle.battery_capacity_kwh,
        )

        # TODO: Persist ChargingSlot records for each selected slot
        # TODO: Send OCPP command to initiate charging

        session.status = "scheduled"
        db.commit()
        return {"session_id": session_id, "slots_scheduled": len(slots)}
    finally:
        db.close()
