import pytest
from datetime import date

POLICY_URL = "/api/policies"
CLAIM_URL = "/api/claims/"
CARS_URL = "/api/cars/"

@pytest.mark.asyncio
async def test_car_delete_cascade(async_client, car_factory):
    car = car_factory()
    # Create a policy
    p_payload = {
        "carId": car.id,
        "provider": "CascadeCo",
        "startDate": date.today().isoformat(),
        "endDate": date.today().isoformat()
    }
    pr = await async_client.post(POLICY_URL, json=p_payload)
    assert pr.status_code == 201
    # Create a claim
    c_payload = {
        "carId": car.id,
        "claimDate": date.today().isoformat(),
        "description": "Test claim",
        "amount": 50
    }
    cr = await async_client.post(CLAIM_URL, json=c_payload)
    assert cr.status_code == 201
    # Delete car
    dr = await async_client.delete(f"{CARS_URL}{car.id}")
    assert dr.status_code == 200
    msg = dr.json()
    assert msg.get("status") == 200 and msg.get("title") == "Deleted" and f"Car {car.id}" in msg.get("detail", "")
    # Policies list should not include policy
    list_policies = await async_client.get(POLICY_URL)
    assert all(p["carId"] != car.id for p in list_policies.json())
    list_claims = await async_client.get(CLAIM_URL)
    assert all(c["carId"] != car.id for c in list_claims.json())
