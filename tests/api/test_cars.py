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
