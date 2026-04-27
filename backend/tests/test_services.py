"""Tests for tariff_service mock price data."""
from datetime import datetime, timedelta
import pytest
from app.services.tariff_service import get_mock_prices, TariffPrice


class TestGetMockPrices:
    def test_returns_list_of_tariff_prices(self):
        from_dt = datetime(2024, 1, 15, 0, 0, 0)
        to_dt = datetime(2024, 1, 15, 2, 0, 0)
        prices = get_mock_prices(from_dt, to_dt)
        assert isinstance(prices, list)
        assert all(isinstance(p, TariffPrice) for p in prices)

    def test_prices_are_30_minute_slots(self):
        from_dt = datetime(2024, 1, 15, 6, 0, 0)
        to_dt = datetime(2024, 1, 15, 8, 0, 0)
        prices = get_mock_prices(from_dt, to_dt)
        assert len(prices) > 0
        for p in prices:
            delta = (p.slot_end - p.slot_start).total_seconds()
            assert delta == 1800, f"Expected 30-min slot, got {delta}s"

    def test_prices_within_realistic_range(self):
        from_dt = datetime(2024, 1, 15, 0, 0, 0)
        to_dt = datetime(2024, 1, 16, 0, 0, 0)
        prices = get_mock_prices(from_dt, to_dt)
        assert len(prices) == 48  # 24 hours * 2 slots/hour
        for p in prices:
            assert p.price_per_kwh > 0, "Price must be positive"
            assert p.price_per_kwh < 100, "Price must be below £1/kWh"

    def test_from_to_bounds_respected(self):
        from_dt = datetime(2024, 1, 15, 10, 0, 0)
        to_dt = datetime(2024, 1, 15, 12, 0, 0)
        prices = get_mock_prices(from_dt, to_dt)
        assert len(prices) > 0
        for p in prices:
            assert p.slot_start >= from_dt.replace(second=0, microsecond=0)
            assert p.slot_end <= to_dt + timedelta(minutes=30)

    def test_returns_empty_list_when_range_zero(self):
        from_dt = datetime(2024, 1, 15, 10, 0, 0)
        to_dt = datetime(2024, 1, 15, 10, 0, 0)
        prices = get_mock_prices(from_dt, to_dt)
        assert prices == []

    def test_region_parameter_accepted(self):
        from_dt = datetime(2024, 1, 15, 0, 0, 0)
        to_dt = datetime(2024, 1, 15, 1, 0, 0)
        prices_c = get_mock_prices(from_dt, to_dt, region="C")
        prices_a = get_mock_prices(from_dt, to_dt, region="A")
        # Both should return slots (mock doesn't differentiate region yet)
        assert len(prices_c) == len(prices_a)

    def test_slot_start_end_are_contiguous(self):
        from_dt = datetime(2024, 1, 15, 0, 0, 0)
        to_dt = datetime(2024, 1, 15, 3, 0, 0)
        prices = get_mock_prices(from_dt, to_dt)
        for i in range(len(prices) - 1):
            assert prices[i].slot_end == prices[i + 1].slot_start
