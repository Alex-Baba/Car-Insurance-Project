from app.db.base import datab as db
from app.db.models import Claims, Car
from app.api.errors import NotFoundError
from app.core.logging import get_logger

log = get_logger()

def list_claims():
    return Claims.query.all()

def create_claim(claim_date, description: str, amount, car_id: int):
    car = Car.query.get(car_id)
    if not car:
        raise NotFoundError("Car not found")
    claim = Claims(claim_date=claim_date, description=description, amount=amount, car_id=car_id)
    db.session.add(claim)
    db.session.commit()
    log.info("claim.created", claim_id=claim.id, car_id=car_id, amount=str(amount), claim_date=claim_date.isoformat())
    return claim