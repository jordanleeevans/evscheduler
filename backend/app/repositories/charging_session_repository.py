from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChargingSession
from app.models.charging_session import SessionStatus


class ChargingSessionRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_all(self) -> list[ChargingSession]:
        result = await self._db.execute(select(ChargingSession))
        return list(result.scalars().all())

    async def get_by_id(self, session_id: int) -> ChargingSession | None:
        result = await self._db.execute(
            select(ChargingSession).where(ChargingSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        vehicle_id: int,
        departure_time: datetime,
        target_charge_pct: float,
    ) -> ChargingSession:
        session = ChargingSession(
            vehicle_id=vehicle_id,
            departure_time=departure_time,
            target_charge_pct=target_charge_pct,
            status=SessionStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(session)
        await self._db.commit()
        await self._db.refresh(session)
        return session

    async def cancel(self, session_id: int) -> ChargingSession | None:
        session = await self.get_by_id(session_id)
        if session:
            session.status = SessionStatus.CANCELLED
            await self._db.commit()
            await self._db.refresh(session)
        return session
