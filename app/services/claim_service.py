from app.db.base import datab as db
from app.db.models import Claim, Car
from app.api.errors import NotFoundError

def list_claims():
    """Return all claims (unfiltered)."""
    return Claim.query.all()

def create_claim(claim_date, description, amount, car_id):
    """Validate car existence and persist a new claim."""
    car = db.session.get(Car, car_id)
    if not car:
        raise NotFoundError("Car not found")
    c = Claim(claim_date=claim_date, description=description, amount=amount, car_id=car_id)
    db.session.add(c)
    db.session.commit()
    return c

def get_claim(claim_id: int):
    """Fetch a single claim by id or raise NotFoundError."""
    c = db.session.get(Claim, claim_id)
    if not c:
        raise NotFoundError("Claim not found")
    return c

def delete_claim(claim_id: int):
    """Delete a claim by id."""
    c = get_claim(claim_id)
    db.session.delete(c)
    db.session.commit()

def get_claims_for_car(car_id: int):
    """Return all claims for a given car id."""
    car = db.session.get(Car, car_id)
    if not car:
        raise NotFoundError("Car not found")
    return Claim.query.filter_by(car_id=car_id).all()