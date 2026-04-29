"""Tests for GraphQL resolvers via HTTPX AsyncClient."""
from datetime import datetime


async def gql_post(client, query: str, variables: dict = None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = await client.post("/graphql", json=payload)
    assert response.status_code == 200
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
        from_dt = datetime(2024, 1, 15, 0, 0, 0).isoformat()
        to_dt = datetime(2024, 1, 15, 4, 0, 0).isoformat()
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
