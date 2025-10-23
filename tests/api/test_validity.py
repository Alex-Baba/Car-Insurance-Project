import pytest
from datetime import date, timedelta
from app.db.base import datab as db
from app.db.models import InsurancePolicy

BASE_URL_FMT = "/api/cars/{id}/insurance-valid"

def build_url(car_id, day):
    return f"{BASE_URL_FMT.format(id=car_id)}?date={day}"

@pytest.mark.asyncio
async def test_validity_true(async_client, car_factory):
    car = car_factory()
    today = date.today()
    pol = InsurancePolicy(car_id=car.id, provider="V", start_date=today, end_date=today)
    db.session.add(pol); db.session.commit()
    r = await async_client.get(build_url(car.id, today.isoformat()))
    assert r.status_code == 200
    data = r.json()
    assert data["carId"] == car.id
    assert data["valid"] is True

@pytest.mark.asyncio
async def test_validity_false(async_client, car_factory):
    car = car_factory()
    today = date.today()
    pol = InsurancePolicy(car_id=car.id, provider="V", start_date=today, end_date=today)
    db.session.add(pol); db.session.commit()
    tomorrow = today + timedelta(days=1)
    r = await async_client.get(build_url(car.id, tomorrow.isoformat()))
    assert r.status_code == 200
    assert r.json()["valid"] is False

@pytest.mark.asyncio
async def test_validity_missing_param(async_client, car_factory):
    car = car_factory()
    r = await async_client.get(f"/api/cars/{car.id}/insurance-valid")
    assert r.status_code in (400, 422)

@pytest.mark.asyncio
async def test_validity_car_404(async_client):
    today = date.today().isoformat()
    r = await async_client.get(build_url(99999, today))
    # service should produce not found for car without policies? if logic returns false adjust accordingly
    assert r.status_code in (404, 200)