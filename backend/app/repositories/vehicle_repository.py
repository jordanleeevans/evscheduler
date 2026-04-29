from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Vehicle


class VehicleRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_all(self) -> list[Vehicle]:
        result = await self._db.execute(select(Vehicle))
        return list(result.scalars().all())

    async def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        result = await self._db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        battery_capacity_kwh: float,
        current_battery_pct: float,
    ) -> Vehicle:
        vehicle = Vehicle(
            name=name,
            battery_capacity_kwh=battery_capacity_kwh,
            current_battery_pct=current_battery_pct,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(vehicle)
        await self._db.commit()
        await self._db.refresh(vehicle)
        return vehicle

    async def update_battery_level(
        self, vehicle_id: int, current_battery_pct: float
    ) -> Vehicle | None:
        vehicle = await self.get_by_id(vehicle_id)
        if vehicle:
            vehicle.current_battery_pct = current_battery_pct
            await self._db.commit()
            await self._db.refresh(vehicle)
        return vehicle
