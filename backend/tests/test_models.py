"""Tests for ORM models: create, persist, and query back."""
from datetime import datetime, timezone, timedelta
from app.models import Vehicle, ChargingSession, Tariff, ChargingSlot
from app.models.charging_session import SessionStatus


class TestVehicle:
    def test_create_vehicle(self, db):
        vehicle = Vehicle(
            name="Tesla Model 3",
            battery_capacity_kwh=75.0,
            current_battery_pct=50.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)

        assert vehicle.id is not None
        assert vehicle.name == "Tesla Model 3"
        assert vehicle.battery_capacity_kwh == 75.0
        assert vehicle.current_battery_pct == 50.0
        assert vehicle.created_at is not None

    def test_query_vehicle(self, db):
        vehicle = Vehicle(
            name="Nissan Leaf",
            battery_capacity_kwh=40.0,
            current_battery_pct=20.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(vehicle)
        db.commit()

        fetched = db.query(Vehicle).filter(Vehicle.name == "Nissan Leaf").first()
        assert fetched is not None
        assert fetched.battery_capacity_kwh == 40.0

    def test_multiple_vehicles(self, db):
        for i in range(3):
            db.add(Vehicle(
                name=f"Car {i}",
                battery_capacity_kwh=60.0,
                current_battery_pct=float(i * 10),
                created_at=datetime.now(timezone.utc),
            ))
        db.commit()
        assert db.query(Vehicle).count() == 3


class TestChargingSession:
    def test_create_session(self, db):
        vehicle = Vehicle(
            name="BMW i3",
            battery_capacity_kwh=42.0,
            current_battery_pct=30.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(vehicle)
        db.commit()

        session = ChargingSession(
            vehicle_id=vehicle.id,
            departure_time=datetime.now(timezone.utc) + timedelta(hours=8),
            target_charge_pct=80.0,
            status=SessionStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        assert session.id is not None
        assert session.vehicle_id == vehicle.id
        assert session.status == SessionStatus.PENDING
        assert session.target_charge_pct == 80.0

    def test_session_status_values(self, db):
        vehicle = Vehicle(
            name="VW ID.4",
            battery_capacity_kwh=77.0,
            current_battery_pct=55.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(vehicle)
        db.commit()

        for status in [SessionStatus.PENDING, SessionStatus.SCHEDULED, SessionStatus.ACTIVE, SessionStatus.COMPLETED, SessionStatus.CANCELLED]:
            session = ChargingSession(
                vehicle_id=vehicle.id,
                departure_time=datetime.now(timezone.utc) + timedelta(hours=4),
                target_charge_pct=90.0,
                status=status,
                created_at=datetime.now(timezone.utc),
            )
            db.add(session)
        db.commit()

        sessions = db.query(ChargingSession).all()
        assert len(sessions) == 5

class TestTariff:
    def test_create_tariff(self, db):
        now = datetime.now(timezone.utc)
        tariff = Tariff(
            name="Octopus Agile",
            region="C",
            valid_from=now,
            valid_to=now + timedelta(days=1),
            created_at=now,
        )
        db.add(tariff)
        db.commit()
        db.refresh(tariff)

        assert tariff.id is not None
        assert tariff.name == "Octopus Agile"
        assert tariff.region == "C"

    def test_query_tariff(self, db):
        now = datetime.now(timezone.utc)
        db.add(Tariff(
            name="GO Tariff",
            region="A",
            valid_from=now,
            valid_to=now + timedelta(hours=4),
            created_at=now,
        ))
        db.commit()

        fetched = db.query(Tariff).filter(Tariff.region == "A").first()
        assert fetched is not None
        assert fetched.name == "GO Tariff"


class TestChargingSlot:
    def test_create_charging_slot(self, db):
        vehicle = Vehicle(
            name="Audi e-tron",
            battery_capacity_kwh=95.0,
            current_battery_pct=40.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(vehicle)
        db.commit()

        session = ChargingSession(
            vehicle_id=vehicle.id,
            departure_time=datetime.now(timezone.utc) + timedelta(hours=6),
            target_charge_pct=85.0,
            status=SessionStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        db.add(session)
        db.commit()

        now = datetime.now(timezone.utc)
        slot = ChargingSlot(
            session_id=session.id,
            slot_start=now,
            slot_end=now + timedelta(minutes=30),
            price_per_kwh=8.5,
            is_selected=True,
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)

        assert slot.id is not None
        assert slot.price_per_kwh == 8.5
        assert slot.is_selected is True
        assert slot.session_id == session.id

    def test_slot_default_not_selected(self, db):
        vehicle = Vehicle(
            name="Hyundai Ioniq 5",
            battery_capacity_kwh=72.6,
            current_battery_pct=25.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(vehicle)
        db.commit()

        session = ChargingSession(
            vehicle_id=vehicle.id,
            departure_time=datetime.now(timezone.utc) + timedelta(hours=5),
            target_charge_pct=80.0,
            status=SessionStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        db.add(session)
        db.commit()

        now = datetime.now(timezone.utc)
        slot = ChargingSlot(
            session_id=session.id,
            slot_start=now,
            slot_end=now + timedelta(minutes=30),
            price_per_kwh=12.0,
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)

        assert slot.is_selected is False
