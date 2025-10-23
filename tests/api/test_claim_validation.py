import pytest
from datetime import date


@pytest.mark.asyncio
async def test_claim_amount_zero(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "claimDate": date.today().isoformat(),
        "description": "Zero amount",
        "amount": 0
    }
    r = await async_client.post("/api/claims/", json=payload)
    assert r.status_code in (400, 422)

@pytest.mark.asyncio
async def test_claim_amount_negative(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "claimDate": date.today().isoformat(),
        "description": "Negative amount",
        "amount": -10
    }
    r = await async_client.post("/api/claims/", json=payload)
    assert r.status_code in (400, 422)

@pytest.mark.asyncio
async def test_claim_empty_description(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "claimDate": date.today().isoformat(),
        "description": "   ",
        "amount": 50
    }
    r = await async_client.post("/api/claims/", json=payload)
    assert r.status_code in (400, 422)
