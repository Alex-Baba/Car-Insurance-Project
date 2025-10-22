from app.db.base import datab as db
from app.db.models import InsurancePolicy, Car
from app.api.errors import NotFoundError
from marshmallow import ValidationError

def list_policies():
    return InsurancePolicy.query.all()

def create_policy(data: dict):
    car = Car.query.get(data["car_id"])
    if not car:
        raise NotFoundError("Car not found")
    if data["end_date"] < data["start_date"]:
        raise ValidationError({"end_date": ["end_date must be >= start_date"]})
    policy = InsurancePolicy(**data)
    db.session.add(policy)
    db.session.commit()
    return policy