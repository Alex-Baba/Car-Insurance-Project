import pytest
from datetime import date, timedelta

POLICY_URL = "/api/cars/policies/"

@pytest.mark.asyncio
async def test_policy_overlap_rejected(async_client, car_factory):
    car = car_factory()
    today = date.today()
    # First policy
    p1 = {
        "carId": car.id,
        "provider": "A",
        "startDate": today.isoformat(),
        "endDate": (today + timedelta(days=5)).isoformat()
    }
    r1 = await async_client.post(POLICY_URL, json=p1)
    assert r1.status_code == 201
    # Overlapping second policy
    p2 = {
        "carId": car.id,
        "provider": "B",
        "startDate": (today + timedelta(days=3)).isoformat(),
        "endDate": (today + timedelta(days=10)).isoformat()
    }
    r2 = await async_client.post(POLICY_URL, json=p2)
    assert r2.status_code in (400, 422)

@pytest.mark.asyncio
async def test_policy_non_overlap_allowed(async_client, car_factory):
    car = car_factory()
    today = date.today()
    p1 = {
        "carId": car.id,
        "provider": "A",
        "startDate": today.isoformat(),
        "endDate": (today + timedelta(days=5)).isoformat()
    }
    r1 = await async_client.post(POLICY_URL, json=p1)
    assert r1.status_code == 201
    # Non-overlapping (starts day after previous end)
    p2 = {
        "carId": car.id,
        "provider": "B",
        "startDate": (today + timedelta(days=6)).isoformat(),
        "endDate": (today + timedelta(days=12)).isoformat()
    }
    r2 = await async_client.post(POLICY_URL, json=p2)
    assert r2.status_code == 201
