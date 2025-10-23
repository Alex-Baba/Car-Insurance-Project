import pytest

@pytest.mark.asyncio
async def test_validity_date_out_of_range(async_client, car_factory):
    car = car_factory()
    # Year beyond allowed upper bound
    r = await async_client.get(f"/api/cars/{car.id}/insurance-valid?date=2101-01-01")
    assert r.status_code in (400, 422)
