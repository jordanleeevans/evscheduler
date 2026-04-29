from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class Tariff(Base):
    """ORM model representing a tariff plan (e.g. Octopus Agile)."""

    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g. "Octopus Agile"
    region = Column(String, nullable=False)  # e.g. "C"
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_to = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
