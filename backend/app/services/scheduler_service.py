"""
Scheduler service: selects the cheapest available charging slots for a session.

Business logic TODO: implement find_cheapest_slots.
"""
from datetime import datetime
from typing import List
from .tariff_service import TariffPrice, get_mock_prices


def find_cheapest_slots(
    departure_time: datetime,
    current_battery_pct: float,
    target_charge_pct: float,
    battery_capacity_kwh: float,
    charger_power_kw: float = 7.4,
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
    now = datetime.utcnow()
    available_prices = get_mock_prices(now, departure_time, region)
    # TODO: calculate energy_needed_kwh, slots_needed, sort by price, select cheapest
    return []
