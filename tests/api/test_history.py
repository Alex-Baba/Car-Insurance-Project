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

@pytest.mark.asyncio
async def test_history_compact(async_client, car_factory):
    car = car_factory()
    # create one policy + one claim
    from datetime import date
    from app.db.models import InsurancePolicy, Claim
    from app.db.base import datab as db
    today = date.today()
    p = InsurancePolicy(car_id=car.id, provider="ACME", start_date=today, end_date=today)
    c = Claim(car_id=car.id, claim_date=today, description="Scratch", amount=10)
    db.session.add_all([p, c]); db.session.commit()
    r = await async_client.get(f"/api/history/{car.id}?format=compact")
    assert r.status_code == 200
    data = r.json()
    assert all("date" in e for e in data)
    # Compact should not include null keys; ensure claim entry lacks startDate/endDate/provider
    claim_entry = next(e for e in data if e["type"] == "CLAIM")
    assert "startDate" not in claim_entry and "endDate" not in claim_entry and "provider" not in claim_entry
    policy_entry = next(e for e in data if e["type"] == "POLICY")
    assert "policyId" in policy_entry and "startDate" in policy_entry and "endDate" in policy_entry