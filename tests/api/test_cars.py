import pytest


@pytest.mark.asyncio
async def test_list_cars(async_client, car_factory):
    car = car_factory()  # ensures at least one car with owner
    r = await async_client.get("/api/cars/")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(c["id"] == car.id for c in data)
    # Verify owner embedded keys if present
    target = next(c for c in data if c["id"] == car.id)
    assert "owner" in target and target["owner"]["id"] == car.owner_id

@pytest.mark.asyncio
async def test_get_car_detail_404(async_client):
    r = await async_client.get("/api/cars/999999")
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_create_car_camelcase(async_client, owner_factory):
    owner = owner_factory()
    payload = {
        "vin": "VIN_CAMELCASE_001",
        "make": "Honda",
        "model": "Civic",
        "yearOfManufacture": 2024,
        "ownerId": owner.id
    }
    r = await async_client.post("/api/cars/", json=payload)
    assert r.status_code == 201, r.text
    assert "Location" in r.headers
    data = r.json()
    assert data["vin"] == payload["vin"]
    assert data["yearOfManufacture"] == 2024
    assert data["ownerId"] == owner.id
