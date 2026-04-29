import enum

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class SessionStatus(enum.Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ChargingSession(Base):
    """ORM model representing a planned charging session for a vehicle."""

    __tablename__ = "charging_sessions"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    target_charge_pct = Column(Float, nullable=False)  # 0-100
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.PENDING)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    vehicle = relationship("Vehicle", back_populates=None)
    slots = relationship("ChargingSlot", back_populates="session")
