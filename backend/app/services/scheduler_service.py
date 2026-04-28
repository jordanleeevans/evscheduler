"""
Scheduler service: selects the cheapest available charging slots for a session.

Business logic TODO: implement find_cheapest_slots.
"""
from datetime import datetime, timezone
from math import ceil
from operator import attrgetter
from typing import List

from pydantic import BaseModel, Field
from .tariff_service import TariffPrice, create_half_hourly_tariffs

class TimeToCharge(BaseModel):
    hours: float = Field(ge=0, description="Hours required to charge.")
    minutes: float = Field(ge=0, description="Minuted required to charge.")


def lt_departure_time(slot_end: datetime, departure_time: datetime) -> bool:
    """Helper function to check if a slot ends before the departure time."""
    return slot_end < departure_time

def available_tariffs_before_departure(available_prices: List[TariffPrice], departure_time: datetime) -> List[TariffPrice]:
    """Filter available tariff prices to those that end before the departure time."""
    return list(filter(lambda p: lt_departure_time(p.slot_end, departure_time), available_prices))

def time_to_charge(departure_time: datetime, current_battery_pct: float, target_charge_pct: float, battery_capacity_kwh: float, charger_power_kw: float) -> TimeToCharge:
    required_pct = target_charge_pct - current_battery_pct

    if required_pct <= 0:
        raise ValueError("Vehicle doesn't require charge.")

    required_energy = battery_capacity_kwh * required_pct / 100 # kwh
    time_to_charge_hours = required_energy / charger_power_kw
    time_to_charge_minutes = time_to_charge_hours * 60
    return TimeToCharge(hours=time_to_charge_hours, minutes=time_to_charge_minutes)

def find_cheapest_slots(
    departure_time: datetime,
    current_battery_pct: float,
    target_charge_pct: float,
    battery_capacity_kwh: float,
    charger_power_kw: float = 7.4,
    starting_time: datetime = None,
    region: str = "C",
) -> List[TariffPrice]:
    """
    Find the cheapest half-hourly slots to charge from current_battery_pct to
    target_charge_pct, completing before departure_time.

    Args:
        departure_time: When the vehicle must be ready.
        current_battery_pct: Current state of charge (0-100).
        target_charge_pct: Desired state of charge at departure (0-100).
        battery_capacity_kwh: Full battery capacity in kWh.
        charger_power_kw: Charger output in kW (default 7.4 kW AC).
        region: Octopus Agile region code.

    Returns:
        Ordered list of selected TariffPrice slots (cheapest first).

    TODO: Implement greedy cheapest-slot selection algorithm.
    """
    # Problem stmt: Given N slots before departure, pick the cheapest M of them.

    TARIFF_FREQUENCY_MINUTES = 30
    now = starting_time or datetime.now(timezone.utc)
    tariff_slots = create_half_hourly_tariffs(now, departure_time, region)
    
    # 1. Get slots < departure_time
    useable_tariffs_slots = available_tariffs_before_departure(tariff_slots, departure_time)

    # 2. Compute required charging time in minutes
    ttc = time_to_charge(departure_time, current_battery_pct, target_charge_pct, battery_capacity_kwh, charger_power_kw)

    required_tariff_slots = ceil(ttc.minutes / TARIFF_FREQUENCY_MINUTES)

    if required_tariff_slots > len(useable_tariffs_slots):
        raise ValueError(f"Not enough available slots to charge vehicle to {target_charge_pct} before {departure_time}.")

    # 3. Sort available slots by price
    ordered_prices_asc = sorted(useable_tariffs_slots, key=attrgetter("price_per_kwh"))

    # 4. Greedily pick cheapest slots until energy requirement is met or we run out of time
    selected_slots = list(ordered_prices_asc)[:required_tariff_slots]
    return selected_slots
