from sqlalchemy import Column, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ChargingSlot(Base):
    """ORM model representing a 30-minute charging slot within a session."""

    __tablename__ = "charging_slots"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("charging_sessions.id"), nullable=False)
    slot_start = Column(DateTime, nullable=False)
    slot_end = Column(DateTime, nullable=False)
    price_per_kwh = Column(Float, nullable=False)
    is_selected = Column(Boolean, default=False, nullable=False)

    session = relationship("ChargingSession", back_populates="slots")
