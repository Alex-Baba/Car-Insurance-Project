from app.db.base import datab as db
from app.db.models import Car, Owner
from app.api.errors import NotFoundError

def list_cars():
    return Car.query.all()

def create_car(vin, make, model, year_of_manufacture, owner_id):
    owner = Owner.query.get(owner_id)
    if not owner:
        raise NotFoundError("Owner not found")
    car = Car(
        vin=vin,
        make=make,
        model=model,
        year_of_manufacture=year_of_manufacture,
        owner_id=owner_id
    )
    db.session.add(car)
    db.session.commit()
    return car

def get_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        raise NotFoundError("Car not found")
    return car

def update_car(car_id, **fields):
    car = get_car(car_id)
    for k, v in fields.items():
        if v is not None:
            setattr(car, k, v)
    db.session.commit()
    return car

def delete_car(car_id):
    car = get_car(car_id)
    db.session.delete(car)
    db.session.commit()