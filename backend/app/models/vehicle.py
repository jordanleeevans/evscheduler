from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from ..database import Base


class Vehicle(Base):
    """ORM model representing an electric vehicle."""

    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g. "Tesla Model 3"
    battery_capacity_kwh = Column(Float, nullable=False)
    current_battery_pct = Column(Float, nullable=False)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
