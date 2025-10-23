import httpx
import pytest
from datetime import date

BASE_URL = "/api/claims/"  # trailing slash to avoid 308

@pytest.mark.asyncio
async def test_create_claim_success(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "claimDate": date.today().isoformat(),
        "description": "Minor scratch",
        "amount": 123
    }
    r = await async_client.post(BASE_URL, json=payload)
    assert r.status_code == 201
    assert r.json()["carId"] == car.id

@pytest.mark.asyncio
async def test_create_claim_missing_amount(async_client, car_factory):
    car = car_factory()
    payload = {
        "carId": car.id,
        "claimDate": date.today().isoformat(),
        "description": "Missing amount"
    }
    r = await async_client.post(BASE_URL, json=payload)
    assert r.status_code in (400, 422)

@pytest.mark.asyncio
async def test_create_claim_car_404(async_client):
    payload = {
        "carId": 99999,
        "claimDate": date.today().isoformat(),
        "description": "Bad car",
        "amount": 10
    }
    r = await async_client.post(BASE_URL, json=payload)
    assert r.status_code == 404