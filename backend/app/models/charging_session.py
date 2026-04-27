from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ChargingSession(Base):
    """ORM model representing a planned charging session for a vehicle."""

    __tablename__ = "charging_sessions"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    target_charge_pct = Column(Float, nullable=False)  # 0-100
    # status: "pending" | "scheduled" | "active" | "completed" | "cancelled"
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    vehicle = relationship("Vehicle", back_populates=None)
    slots = relationship("ChargingSlot", back_populates="session")
