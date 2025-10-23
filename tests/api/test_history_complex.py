import pytest
from datetime import date, timedelta
from app.db.base import datab as db
from app.db.models import InsurancePolicy, Claim


@pytest.mark.asyncio
async def test_history_complex_ordering(async_client, car_factory):
    car = car_factory()
    today = date.today()
    d_minus_3 = today - timedelta(days=3)
    d_minus_2 = today - timedelta(days=2)
    d_minus_1 = today - timedelta(days=1)
    # Policies
    p1 = InsurancePolicy(car_id=car.id, provider="A", start_date=d_minus_3, end_date=d_minus_3)
    p2 = InsurancePolicy(car_id=car.id, provider="B", start_date=d_minus_1, end_date=d_minus_1)
    # Claims interleaved
    c1 = Claim(car_id=car.id, claim_date=d_minus_2, description="Mid", amount=10)
    c2 = Claim(car_id=car.id, claim_date=today, description="Latest", amount=15)
    db.session.add_all([p1, p2, c1, c2]); db.session.commit()
    r = await async_client.get(f"/api/history/{car.id}")
    assert r.status_code == 200
    data = r.json()
    # Extract chronological key
    chrono = []
    for e in data:
        chrono.append(e.get("startDate") or e.get("claimDate") or e.get("endDate"))
    # Convert to tuple of (index, date) and assert sorted ascending
    iso_sorted = sorted(chrono)
    assert chrono == iso_sorted, f"History not chronological: {chrono}"
    # Ensure both policy and claim types present
    types = {e["type"] for e in data}
    assert {"POLICY", "CLAIM"}.issubset(types)

@pytest.mark.asyncio
async def test_history_404(async_client):
    r = await async_client.get("/api/history/999999")
    assert r.status_code == 404
