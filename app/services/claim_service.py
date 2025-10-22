from app.db.base import datab as db
from app.db.models import Claims, Car
from app.api.errors import NotFoundError

def list_claims():
    return Claims.query.all()

def create_claim(data: dict):
    car = Car.query.get(data["car_id"])
    if not car:
        raise NotFoundError("Car not found")
    claim = Claims(**data)
    db.session.add(claim)
    db.session.commit()
    return claim