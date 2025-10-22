from app.db.base import datab as db
from app.db.models import Car, Owner
from app.api.errors import NotFoundError

def create_car(data):
    owner = Owner.query.get(data["owner_id"])
    if not owner:
        raise NotFoundError("Owner not found")
    car = Car(
        vin=data["vin"],
        make=data["make"],
        model=data["model"],
        year_of_manufacture=data["year_of_manufacture"],
        owner_id=data["owner_id"]
    )
    db.session.add(car)
    db.session.commit()
    return car

def get_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        raise NotFoundError("Car not found")
    return car

def delete_car(car_id):
    car = get_car(car_id)
    db.session.delete(car)
    db.session.commit()

def list_cars():
    return Car.query.all()