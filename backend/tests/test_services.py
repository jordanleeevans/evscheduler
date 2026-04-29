"""Tests for tariff_service mock price data."""

from datetime import datetime, timedelta, timezone
from math import ceil
from app.services.tariff_service import create_half_hourly_tariffs, TariffPrice
from app.services.scheduler_service import (
    available_tariffs_before_departure,
    find_cheapest_slots,
    lt_departure_time,
    time_to_charge,
)


class TestGetMockPrices:
    def test_returns_list_of_tariff_prices(self):
        from_dt = datetime(2024, 1, 15, 0, 0, 0)
        to_dt = datetime(2024, 1, 15, 2, 0, 0)
        prices = create_half_hourly_tariffs(from_dt, to_dt)
        assert isinstance(prices, list)
        assert all(isinstance(p, TariffPrice) for p in prices)

    def test_prices_are_30_minute_slots(self):
        from_dt = datetime(2024, 1, 15, 6, 0, 0)
        to_dt = datetime(2024, 1, 15, 8, 0, 0)
        prices = create_half_hourly_tariffs(from_dt, to_dt)
        assert len(prices) > 0
        for p in prices:
            delta = (p.slot_end - p.slot_start).total_seconds()
            assert delta == 1800, f"Expected 30-min slot, got {delta}s"

    def test_prices_within_realistic_range(self):
        from_dt = datetime(2024, 1, 15, 0, 0, 0)
        to_dt = datetime(2024, 1, 16, 0, 0, 0)
        prices = create_half_hourly_tariffs(from_dt, to_dt)
        assert len(prices) == 48  # 24 hours * 2 slots/hour
        for p in prices:
            assert p.price_per_kwh > 0, "Price must be positive"
            assert p.price_per_kwh < 100, "Price must be below £1/kWh"

    def test_from_to_bounds_respected(self):
        from_dt = datetime(2024, 1, 15, 10, 0, 0)
        to_dt = datetime(2024, 1, 15, 12, 0, 0)
        prices = create_half_hourly_tariffs(from_dt, to_dt)
        assert len(prices) > 0
        for p in prices:
            assert p.slot_start >= from_dt.replace(second=0, microsecond=0)
            assert p.slot_end <= to_dt + timedelta(minutes=30)

    def test_returns_empty_list_when_range_zero(self):
        from_dt = datetime(2024, 1, 15, 10, 0, 0)
        to_dt = datetime(2024, 1, 15, 10, 0, 0)
        prices = create_half_hourly_tariffs(from_dt, to_dt)
        assert prices == []

    def test_region_parameter_accepted(self):
        from_dt = datetime(2024, 1, 15, 0, 0, 0)
        to_dt = datetime(2024, 1, 15, 1, 0, 0)
        prices_c = create_half_hourly_tariffs(from_dt, to_dt, region="C")
        prices_a = create_half_hourly_tariffs(from_dt, to_dt, region="A")
        # Both should return slots (mock doesn't differentiate region yet)
        assert len(prices_c) == len(prices_a)

    def test_slot_start_end_are_contiguous(self):
        from_dt = datetime(2024, 1, 15, 0, 0, 0)
        to_dt = datetime(2024, 1, 15, 3, 0, 0)
        prices = create_half_hourly_tariffs(from_dt, to_dt)
        for i in range(len(prices) - 1):
            assert prices[i].slot_end == prices[i + 1].slot_start


class TestSchedulerService:
    def test_lt_departure_time_true(self):
        slot_end = datetime(2024, 1, 15, 0, 0, 0)
        departure_time = datetime(2024, 1, 15, 1, 0, 0)

        assert lt_departure_time(slot_end, departure_time)

    def test_lt_departure_time_false(self):
        slot_end = datetime(2024, 1, 15, 2, 0, 0)
        departure_time = datetime(2024, 1, 15, 1, 0, 0)

        assert not lt_departure_time(slot_end, departure_time)

    def test_available_tariffs_before_departure_filters_correctly(self):
        now = datetime(2024, 1, 15, 0, 0, 0)
        departure_time = now + timedelta(hours=2)

        slots_that_end_before_departure = [
            TariffPrice(
                slot_start=now + timedelta(minutes=30),
                slot_end=now + timedelta(minutes=60),
                price_per_kwh=10.0,
            ),
        ]

        slots_that_end_after_departure = [
            TariffPrice(
                slot_start=now + timedelta(minutes=90),
                slot_end=now + timedelta(minutes=120),
                price_per_kwh=12.0,
            ),
            TariffPrice(
                slot_start=now + timedelta(minutes=150),
                slot_end=now + timedelta(minutes=180),
                price_per_kwh=8.0,
            ),
        ]

        all_slots = slots_that_end_before_departure + slots_that_end_after_departure

        filtered = available_tariffs_before_departure(all_slots, departure_time)
        assert len(filtered) == 1
        assert filtered[0].slot_end < departure_time

    def test_time_to_charge_calculation(self):
        departure_time = datetime(2024, 1, 15, 8, 0, 0)
        current_battery_pct = 20.0
        target_charge_pct = 80.0
        battery_capacity_kwh = 60.0
        charger_power_kw = 7.4

        ttc = time_to_charge(
            departure_time,
            current_battery_pct,
            target_charge_pct,
            battery_capacity_kwh,
            charger_power_kw,
        )
        expected_required_energy = (
            battery_capacity_kwh * (target_charge_pct - current_battery_pct) / 100
        )  # kWh
        assert round(ttc.hours, 2) == round(
            expected_required_energy / charger_power_kw, 2
        )
        assert ttc.minutes == expected_required_energy / charger_power_kw * 60

    def test_time_to_charge_no_charge_needed(self):
        departure_time = datetime(2024, 1, 15, 8, 0, 0)
        current_battery_pct = 80.0
        target_charge_pct = 80.0
        battery_capacity_kwh = 60.0
        charger_power_kw = 7.4

        try:
            time_to_charge(
                departure_time,
                current_battery_pct,
                target_charge_pct,
                battery_capacity_kwh,
                charger_power_kw,
            )
            assert False, "Expected ValueError for no charge needed"
        except ValueError as e:
            assert str(e) == "Vehicle doesn't require charge."

    def test_not_enough_slots_available(self):
        starting_time = datetime(2024, 1, 15, 9, 0, 0, tzinfo=timezone.utc)
        departure_time = datetime(2024, 1, 15, 8, 0, 0, tzinfo=timezone.utc)

        assert starting_time > departure_time, (
            "Starting time should be before departure time for this test"
        )

        current_battery_pct = 20.0
        target_charge_pct = 80.0
        battery_capacity_kwh = 60.0
        charger_power_kw = 7.4

        try:
            _ = find_cheapest_slots(
                departure_time,
                current_battery_pct,
                target_charge_pct,
                battery_capacity_kwh,
                charger_power_kw=charger_power_kw,
                starting_time=starting_time,
                region="C",
            )
            assert False, "Expected ValueError for not enough available slots"
        except ValueError as e:
            assert "Not enough available slots" in str(e)

    def test_find_cheapest_slots_returns_correct_number_of_slots(self):
        starting_time = datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        departure_time = datetime(2024, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
        current_battery_pct = 20.0
        target_charge_pct = 80.0
        battery_capacity_kwh = 60.0
        charger_power_kw = 7.4

        selected_slots = find_cheapest_slots(
            departure_time,
            current_battery_pct,
            target_charge_pct,
            battery_capacity_kwh,
            charger_power_kw=charger_power_kw,
            starting_time=starting_time,
            region="C",
        )

        ttc = time_to_charge(
            departure_time,
            current_battery_pct,
            target_charge_pct,
            battery_capacity_kwh,
            charger_power_kw,
        )
        required_slots = ceil(ttc.minutes / 30)

        assert len(selected_slots) == required_slots

    def test_find_cheapest_slots_returns_cheapest_slots(self):
        starting_time = datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        departure_time = datetime(2024, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
        current_battery_pct = 20.0
        target_charge_pct = 80.0
        battery_capacity_kwh = 60.0
        charger_power_kw = 7.4

        selected_slots = find_cheapest_slots(
            departure_time,
            current_battery_pct,
            target_charge_pct,
            battery_capacity_kwh,
            starting_time=starting_time,
            charger_power_kw=charger_power_kw,
            region="C",
        )

        # Check that selected slots are cheaper than any unselected slots
        all_slots = create_half_hourly_tariffs(
            starting_time, departure_time, region="C"
        )
        useable_slots = available_tariffs_before_departure(all_slots, departure_time)
        for selected_slot in selected_slots:
            for other_slot in useable_slots:
                if other_slot not in selected_slots:
                    assert selected_slot.price_per_kwh <= other_slot.price_per_kwh
