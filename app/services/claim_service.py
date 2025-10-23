from app.db.base import datab as db
from app.db.models import Claim, Car
from app.api.errors import NotFoundError

def list_claims():
    return Claim.query.all()

def create_claim(claim_date, description, amount, car_id):
    car = db.session.get(Car, car_id)
    if not car:
        raise NotFoundError("Car not found")
    c = Claim(claim_date=claim_date, description=description, amount=amount, car_id=car_id)
    db.session.add(c)
    db.session.commit()
    return c