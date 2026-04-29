"""Tests for GraphQL resolvers via HTTPX AsyncClient."""

from datetime import datetime, timezone, timedelta

from app.models.charging_session import SessionStatus


async def gql_post(client, query: str, variables: dict = None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = await client.post("/graphql", json=payload)
    # 200 = execution result; 400 = validation/coercion error (both return JSON error bodies)
    assert response.status_code in (200, 400), (
        f"Unexpected status: {response.status_code}"
    )
    return response.json()


class TestQueryResolvers:
    async def test_vehicles_returns_empty_list(self, client):
        result = await gql_post(client, "{ vehicles { id name } }")
        assert "errors" not in result
        assert result["data"]["vehicles"] == []

    async def test_charging_sessions_returns_empty_list(self, client):
        result = await gql_post(client, "{ chargingSessions { id status } }")
        assert "errors" not in result
        assert result["data"]["chargingSessions"] == []

    async def test_tariff_prices_returns_non_empty_list(self, client):
        from_dt = datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc).isoformat()
        to_dt = datetime(2024, 1, 15, 4, 0, 0, tzinfo=timezone.utc).isoformat()
        query = f'{{ tariffPrices(from: "{from_dt}", to: "{to_dt}") {{ slotStart pricePerKwh }} }}'
        result = await gql_post(client, query)
        assert "errors" not in result
        prices = result["data"]["tariffPrices"]
        assert len(prices) > 0
        assert "slotStart" in prices[0]
        assert "pricePerKwh" in prices[0]
        assert prices[0]["pricePerKwh"] > 0

    async def test_vehicle_query_returns_none_for_missing_id(self, client):
        result = await gql_post(client, '{ vehicle(id: "9999") { id name } }')
        assert "errors" not in result
        assert result["data"]["vehicle"] is None

    async def test_charging_session_query_returns_none_for_missing_id(self, client):
        result = await gql_post(client, '{ chargingSession(id: "9999") { id status } }')
        assert "errors" not in result
        assert result["data"]["chargingSession"] is None


class TestMutationResolvers:
    async def test_create_vehicle_returns_vehicle_with_correct_fields(self, client):
        mutation = """
        mutation {
            createVehicle(
                name: "Tesla Model 3"
                batteryCapacityKwh: 75.0
                currentBatteryPct: 50.0
            ) {
                id
                name
                batteryCapacityKwh
                currentBatteryPct
                createdAt
            }
        }
        """
        result = await gql_post(client, mutation)
        assert "errors" not in result
        vehicle = result["data"]["createVehicle"]
        assert vehicle["name"] == "Tesla Model 3"
        assert vehicle["batteryCapacityKwh"] == 75.0
        assert vehicle["currentBatteryPct"] == 50.0
        assert vehicle["id"] is not None
        assert vehicle["createdAt"] is not None

    async def test_create_vehicle_then_query_it(self, client):
        mutation = """
        mutation {
            createVehicle(
                name: "Nissan Leaf"
                batteryCapacityKwh: 40.0
                currentBatteryPct: 30.0
            ) { id name }
        }
        """
        result = await gql_post(client, mutation)
        assert "errors" not in result
        vehicle_id = result["data"]["createVehicle"]["id"]

        query = f'{{ vehicle(id: "{vehicle_id}") {{ id name batteryCapacityKwh }} }}'
        result2 = await gql_post(client, query)
        assert "errors" not in result2
        assert result2["data"]["vehicle"]["name"] == "Nissan Leaf"

    async def test_vehicles_list_after_create(self, client):
        mutation = """
        mutation {
            createVehicle(
                name: "Audi e-tron"
                batteryCapacityKwh: 95.0
                currentBatteryPct: 60.0
            ) { id }
        }
        """
        await gql_post(client, mutation)
        result = await gql_post(client, "{ vehicles { id name } }")
        assert len(result["data"]["vehicles"]) == 1
        assert result["data"]["vehicles"][0]["name"] == "Audi e-tron"

    async def test_update_battery_level(self, client):
        create = """
        mutation {
            createVehicle(name: "BMW i3", batteryCapacityKwh: 42.0, currentBatteryPct: 30.0) { id }
        }
        """
        vehicle_id = (await gql_post(client, create))["data"]["createVehicle"]["id"]

        update = f"""
        mutation {{
            updateBatteryLevel(vehicleId: "{vehicle_id}", currentBatteryPct: 85.0) {{
                id currentBatteryPct
            }}
        }}
        """
        result = await gql_post(client, update)
        assert "errors" not in result
        assert result["data"]["updateBatteryLevel"]["currentBatteryPct"] == 85.0

    async def test_schedule_and_cancel_charging_session(self, client):
        create_v = """
        mutation {
            createVehicle(name: "VW ID.4", batteryCapacityKwh: 77.0, currentBatteryPct: 55.0) { id }
        }
        """
        vehicle_id = (await gql_post(client, create_v))["data"]["createVehicle"]["id"]

        departure = (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat()
        schedule = f"""
        mutation {{
            scheduleChargingSession(
                vehicleId: "{vehicle_id}",
                departureTime: "{departure}",
                targetChargePct: 80.0
            ) {{ id status }}
        }}
        """
        result = await gql_post(client, schedule)
        assert "errors" not in result
        session = result["data"]["scheduleChargingSession"]
        assert session["status"] == "PENDING"

        cancel = f'mutation {{ cancelChargingSession(id: "{session["id"]}") {{ id status }} }}'
        cancel_result = await gql_post(client, cancel)
        assert "errors" not in cancel_result
        assert (
            cancel_result["data"]["cancelChargingSession"]["status"]
            == SessionStatus.CANCELLED.value
        )


class TestValidation:
    async def test_percentage_above_100_is_rejected(self, client):
        mutation = """
        mutation {
            createVehicle(name: "X", batteryCapacityKwh: 60.0, currentBatteryPct: 150.0) { id }
        }
        """
        result = await gql_post(client, mutation)
        assert "errors" in result

    async def test_percentage_below_0_is_rejected(self, client):
        mutation = """
        mutation {
            createVehicle(name: "X", batteryCapacityKwh: 60.0, currentBatteryPct: -5.0) { id }
        }
        """
        result = await gql_post(client, mutation)
        assert "errors" in result

    async def test_datetime_without_timezone_is_rejected(self, client):
        mutation = """
        mutation {
            scheduleChargingSession(
                vehicleId: "1",
                departureTime: "2099-01-01T08:00:00",
                targetChargePct: 80.0
            ) { id }
        }
        """
        result = await gql_post(client, mutation)
        assert "errors" in result

    async def test_schedule_session_with_nonexistent_vehicle_raises_error(self, client):
        departure = (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()
        mutation = f"""
        mutation {{
            scheduleChargingSession(
                vehicleId: "9999",
                departureTime: "{departure}",
                targetChargePct: 80.0
            ) {{ id }}
        }}
        """
        result = await gql_post(client, mutation)
        assert "errors" in result
        assert "not found" in result["errors"][0]["message"]

    async def test_schedule_session_with_past_departure_raises_error(self, client):
        create_v = """
        mutation {
            createVehicle(name: "Test Car", batteryCapacityKwh: 60.0, currentBatteryPct: 50.0) { id }
        }
        """
        vehicle_id = (await gql_post(client, create_v))["data"]["createVehicle"]["id"]

        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        mutation = f"""
        mutation {{
            scheduleChargingSession(
                vehicleId: "{vehicle_id}",
                departureTime: "{past}",
                targetChargePct: 80.0
            ) {{ id }}
        }}
        """
        result = await gql_post(client, mutation)
        assert "errors" in result
        assert "future" in result["errors"][0]["message"]

    async def test_cancel_nonexistent_session_raises_error(self, client):
        result = await gql_post(
            client, 'mutation { cancelChargingSession(id: "9999") { id } }'
        )
        assert "errors" in result
        assert "not found" in result["errors"][0]["message"]

    async def test_update_battery_for_nonexistent_vehicle_raises_error(self, client):
        result = await gql_post(
            client,
            'mutation { updateBatteryLevel(vehicleId: "9999", currentBatteryPct: 50.0) { id } }',
        )
        assert "errors" in result
        assert "not found" in result["errors"][0]["message"]

    async def test_battery_capacity_must_be_positive(self, client):
        mutation = """
        mutation {
            createVehicle(name: "X", batteryCapacityKwh: -10.0, currentBatteryPct: 50.0) { id }
        }
        """
        result = await gql_post(client, mutation)
        assert "errors" in result
