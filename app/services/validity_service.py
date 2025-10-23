from app.db.models import InsurancePolicy, Car
from app.api.errors import NotFoundError
from datetime import date
from app.core.logging import get_logger

log = get_logger()

def check_insurance(car_id: int, target_date: date):
    """Return whether a car has an active policy covering target_date with logging metadata."""
    from app.db.base import datab as db
    car = db.session.get(Car, car_id)
    if not car:
        raise NotFoundError("Car not found")
    policy = InsurancePolicy.query.filter(
        InsurancePolicy.car_id == car_id,
        InsurancePolicy.start_date <= target_date,
        InsurancePolicy.end_date >= target_date
    ).first()
    valid = bool(policy)
    log.info("insurance.check", car_id=car_id, date=target_date.isoformat(), valid=valid,
             policy_id=policy.id if policy else None)
    return {
        "carId": car_id,
        "date": target_date,
        "valid": valid
    }