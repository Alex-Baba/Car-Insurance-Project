import pytest
from datetime import date


@pytest.mark.asyncio
async def test_policy_end_date_before_start(async_client, car_factory):
    car = car_factory()
    today = date.today()
    payload = {
        "carId": car.id,
        "provider": "TestCo",
        "startDate": today.isoformat(),
        "endDate": (today.replace(day=today.day - 1)).isoformat() if today.day > 1 else today.isoformat()
    }
    # If startDate == endDate due to day==1, fudge by subtracting one day via a fixed earlier date
    if payload["startDate"] == payload["endDate"]:
        payload["endDate"] = "1899-12-31"  # guaranteed before start
    r = await async_client.post("/api/policies", json=payload)
    assert r.status_code in (400, 422)

@pytest.mark.asyncio
async def test_policy_date_out_of_range(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "provider": "Legacy",
        "startDate": "1899-01-01",
        "endDate": "1899-12-31"
    }
    r = await async_client.post("/api/policies", json=payload)
    assert r.status_code in (400, 422)
