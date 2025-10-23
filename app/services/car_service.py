from app.db.base import datab as db
from app.db.models import Car, Owner
from app.api.errors import NotFoundError, ConflictError
from sqlalchemy.exc import IntegrityError

def list_cars():
    """Return all cars (no pagination yet)."""
    return Car.query.all()

def create_car(data: dict):
    """Create a new car ensuring the referenced owner exists.

    Expects dict with keys vin, make, model, year_of_manufacture, owner_id.
    Raises NotFoundError if owner missing; ConflictError if VIN duplicate.
    """
    owner_id = data.get("owner_id")
    owner = db.session.get(Owner, owner_id)
    if not owner:
        raise NotFoundError("Owner not found")
    car = Car(
        vin=data.get("vin"),
        make=data.get("make"),
        model=data.get("model"),
        year_of_manufacture=data.get("year_of_manufacture"),
        owner_id=owner_id
    )
    db.session.add(car)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError("VIN already exists")
    return car

def get_car(car_id):
    """Fetch a car by id or raise NotFoundError."""
    car = db.session.get(Car, car_id)
    if not car:
        raise NotFoundError("Car not found")
    return car

def update_car(car_id, **fields):
    """Update provided (non-None) fields of a car."""
    car = get_car(car_id)
    for k, v in fields.items():
        if v is not None:
            setattr(car, k, v)
    db.session.commit()
    return car

def delete_car(car_id):
    """Delete a car and cascade related policies/claims due to model relationship settings."""
    car = get_car(car_id)
    db.session.delete(car)
    db.session.commit()