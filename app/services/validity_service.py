from app.db.models import InsurancePolicy, Car
from app.api.errors import NotFoundError

def check_insurance(car_id, target_date):
    car = Car.query.get(car_id)
    if not car:
        raise NotFoundError("Car not found")
    policy = InsurancePolicy.query.filter(
        InsurancePolicy.car_id == car_id,
        InsurancePolicy.start_date <= target_date,
        InsurancePolicy.end_date >= target_date
    ).first()
    return bool(policy), policy