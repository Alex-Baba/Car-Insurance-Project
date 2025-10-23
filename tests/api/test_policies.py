import httpx
import pytest
from datetime import date

@pytest.mark.asyncio
async def test_create_policy_success(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "provider": "ACME",
        "startDate": date.today().isoformat(),
        "endDate": date.today().isoformat()
    }
    r = await async_client.post("/api/policies", json=payload)
    assert r.status_code == 201
    assert r.json()["carId"] == car.id

@pytest.mark.asyncio
async def test_create_policy_missing_end_date(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "provider": "ACME",
        "startDate": date.today().isoformat()
    }
    r = await async_client.post("/api/policies", json=payload)
    assert r.status_code in (400, 422)

@pytest.mark.asyncio
async def test_create_policy_null_end_date(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "provider": "ACME",
        "startDate": date.today().isoformat(),
        "endDate": None
    }
    r = await async_client.post("/api/policies", json=payload)
    assert r.status_code in (400, 422)