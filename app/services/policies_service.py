from app.db.base import datab as db
from app.db.models import InsurancePolicy, Car
from app.api.errors import NotFoundError
from pydantic import ValidationError

def list_policies():
    return InsurancePolicy.query.all()

def get_policy(policy_id: int):
    p = InsurancePolicy.query.get(policy_id)
    if not p:
        raise NotFoundError("Policy not found")
    return p

def create_policy(provider, start_date, end_date, car_id):
    car = Car.query.get(car_id)
    if not car:
        raise NotFoundError("Car not found")
    if end_date < start_date:
        raise ValidationError.from_exception_data("endDate", [{
            "loc": ("endDate",),
            "msg": "endDate must be >= startDate",
            "type": "value_error"
        }])
    p = InsurancePolicy(provider=provider, start_date=start_date, end_date=end_date, car_id=car_id)
    db.session.add(p)
    db.session.commit()
    return p

def update_policy(policy_id, provider=None, start_date=None, end_date=None):
    p = get_policy(policy_id)
    new_start = start_date or p.start_date
    new_end = end_date or p.end_date
    if new_end < new_start:
        raise ValidationError.from_exception_data("endDate", [{
            "loc": ("endDate",),
            "msg": "endDate must be >= startDate",
            "type": "value_error"
        }])
    if provider is not None:
        p.provider = provider
    if start_date is not None:
        p.start_date = start_date
    if end_date is not None:
        p.end_date = end_date
    db.session.commit()
    return p