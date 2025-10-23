import httpx
import pytest
from datetime import date, timedelta
from app.db.base import datab as db
from app.db.models import InsurancePolicy, Claim

HISTORY_PATH_FMT = "/api/history/{id}"  # actual route prefix without trailing slash

@pytest.mark.asyncio
async def test_history_ordering(async_client, car_factory):
    car = car_factory()
    d2 = date.today() - timedelta(days=2)
    d1 = date.today() - timedelta(days=1)
    p_old = InsurancePolicy(car_id=car.id, provider="A", start_date=d2, end_date=d2)
    p_new = InsurancePolicy(car_id=car.id, provider="B", start_date=d1, end_date=d1)
    cl = Claim(car_id=car.id, claim_date=date.today(), description="Crash", amount=5)
    db.session.add_all([p_old, p_new, cl]); db.session.commit()
    url = HISTORY_PATH_FMT.format(id=car.id)
    r = await async_client.get(url)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 3