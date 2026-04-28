from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base


class Tariff(Base):
    """ORM model representing a tariff plan (e.g. Octopus Agile)."""

    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)    # e.g. "Octopus Agile"
    region = Column(String, nullable=False)  # e.g. "C"
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
