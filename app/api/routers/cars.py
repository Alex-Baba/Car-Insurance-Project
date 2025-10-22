from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from app.db.base import datab as db
from app.db.models import Car, Owner
from app.api.schemas import CarSchema, CarInputSchema, DeleteCarSchema
from app.api.errors import NotFoundError

bp = Blueprint('cars', __name__, url_prefix='/api/cars')

@bp.route('/')
class CarsCollection(MethodView):
    @bp.response(200, CarSchema(many=True))
    def get(self):
        return Car.query.all()

    @bp.arguments(CarInputSchema)
    @bp.response(201, CarSchema)
    def post(self, data):
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

@bp.route('/<int:car_id>')
class CarItem(MethodView):
    @bp.response(200, CarSchema)
    def get(self, car_id):
        car = Car.query.get(car_id)
        if not car:
            raise NotFoundError("Car not found")
        return car

    @bp.arguments(DeleteCarSchema)
    @bp.response(204)
    def delete(self, data, car_id):
        car = Car.query.get(car_id)
        if not car:
            raise NotFoundError("Car not found")
        db.session.delete(car)
        db.session.commit()
        return ""
