"""
Mock implementation of the Octopus Energy Agile tariff price feed.

The real Octopus Agile API endpoint is:
  https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/

This mock returns deterministic half-hourly prices for a 24-hour window.
"""

from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel
import math


class TariffPrice(BaseModel):
    slot_start: datetime
    slot_end: datetime
    price_per_kwh: float


def create_half_hourly_tariffs(
    from_dt: datetime, to_dt: datetime, region: str = "C"
) -> List[TariffPrice]:
    """Return mock half-hourly Agile tariff prices between from_dt and to_dt.

    Prices follow a realistic overnight dip pattern:
    - Peak: ~30p/kWh during 17:00-20:00
    - Off-peak: ~5p/kWh during 00:30-06:00
    - Uses a sine-wave approximation for demo purposes.

    TODO: Replace with live Octopus Energy API call.
    """
    prices = []
    current = from_dt.replace(
        minute=0 if from_dt.minute < 30 else 30,
        second=0,
        microsecond=0,
    )

    PI = math.pi
    PHASE_SHIFT = 6  # Shift peak to 18:00
    BASE_PRICE = 15.0
    AMPLITUDE = 12.0
    NOISE_AMPLITUDE = 3.0

    while current < to_dt:
        hour = current.hour + current.minute / 60.0
        # Sine-wave based price curve: cheap overnight, expensive evening
        # price = base + amplitude * sin(pi * (hour - shift) / period) + noise
        price = (
            BASE_PRICE
            + AMPLITUDE * math.sin(PI * (hour - PHASE_SHIFT) / 12)
            + NOISE_AMPLITUDE * math.sin(PI * hour / 6)
        )
        price = max(2.0, round(price, 2))
        prices.append(
            TariffPrice(
                slot_start=current,
                slot_end=current + timedelta(minutes=30),
                price_per_kwh=price,
            )
        )
        current += timedelta(minutes=30)
    return prices
