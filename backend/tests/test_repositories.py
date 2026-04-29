"""Tests for repository classes."""

from datetime import datetime, timezone, timedelta
from app.models.charging_session import SessionStatus
from app.repositories import VehicleRepository, ChargingSessionRepository


class TestVehicleRepository:
    async def test_create_returns_vehicle_with_id(self, db):
        repo = VehicleRepository(db)
        vehicle = await repo.create("Tesla Model 3", 75.0, 50.0)

        assert vehicle.id is not None
        assert vehicle.name == "Tesla Model 3"
        assert vehicle.battery_capacity_kwh == 75.0
        assert vehicle.current_battery_pct == 50.0
        assert vehicle.created_at is not None

    async def test_get_by_id_returns_vehicle(self, db):
        repo = VehicleRepository(db)
        created = await repo.create("Nissan Leaf", 40.0, 20.0)

        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.battery_capacity_kwh == 40.0

    async def test_get_by_id_returns_none_for_missing(self, db):
        repo = VehicleRepository(db)
        assert await repo.get_by_id(9999) is None

    async def test_get_all_returns_all_vehicles(self, db):
        repo = VehicleRepository(db)
        await repo.create("Car A", 60.0, 10.0)
        await repo.create("Car B", 60.0, 20.0)
        await repo.create("Car C", 60.0, 30.0)

        vehicles = await repo.get_all()
        assert len(vehicles) == 3

    async def test_get_all_returns_empty_list(self, db):
        repo = VehicleRepository(db)
        assert await repo.get_all() == []

    async def test_update_battery_level(self, db):
        repo = VehicleRepository(db)
        vehicle = await repo.create("BMW i3", 42.0, 30.0)

        updated = await repo.update_battery_level(vehicle.id, 85.0)
        assert updated is not None
        assert updated.current_battery_pct == 85.0

    async def test_update_battery_level_returns_none_for_missing(self, db):
        repo = VehicleRepository(db)
        assert await repo.update_battery_level(9999, 50.0) is None


class TestChargingSessionRepository:
    async def _create_vehicle(self, db):
        return await VehicleRepository(db).create("VW ID.4", 77.0, 55.0)

    async def test_create_returns_session_with_id(self, db):
        vehicle = await self._create_vehicle(db)
        repo = ChargingSessionRepository(db)
        departure = datetime.now(timezone.utc) + timedelta(hours=8)

        session = await repo.create(vehicle.id, departure, 80.0)

        assert session.id is not None
        assert session.vehicle_id == vehicle.id
        assert session.target_charge_pct == 80.0
        assert session.status == SessionStatus.PENDING
        assert session.created_at is not None

    async def test_get_by_id_returns_session(self, db):
        vehicle = await self._create_vehicle(db)
        repo = ChargingSessionRepository(db)
        created = await repo.create(
            vehicle.id, datetime.now(timezone.utc) + timedelta(hours=4), 90.0
        )

        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    async def test_get_by_id_returns_none_for_missing(self, db):
        repo = ChargingSessionRepository(db)
        assert await repo.get_by_id(9999) is None

    async def test_get_all_returns_all_sessions(self, db):
        vehicle = await self._create_vehicle(db)
        repo = ChargingSessionRepository(db)
        departure = datetime.now(timezone.utc) + timedelta(hours=6)
        await repo.create(vehicle.id, departure, 80.0)
        await repo.create(vehicle.id, departure, 90.0)

        sessions = await repo.get_all()
        assert len(sessions) == 2

    async def test_get_all_returns_empty_list(self, db):
        repo = ChargingSessionRepository(db)
        assert await repo.get_all() == []

    async def test_cancel_sets_status_to_cancelled(self, db):
        vehicle = await self._create_vehicle(db)
        repo = ChargingSessionRepository(db)
        session = await repo.create(
            vehicle.id, datetime.now(timezone.utc) + timedelta(hours=5), 75.0
        )

        cancelled = await repo.cancel(session.id)
        assert cancelled is not None
        assert cancelled.status == SessionStatus.CANCELLED

    async def test_cancel_returns_none_for_missing(self, db):
        repo = ChargingSessionRepository(db)
        assert await repo.cancel(9999) is None

