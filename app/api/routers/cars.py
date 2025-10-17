from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import Car
from app.api.schemas import CarSchema
from app.api.schemas import deleteCarSchema



from app.db.base import datab as db

bp = Blueprint('cars', __name__)

@bp.route('/')
class CarsResource(MethodView):
    @bp.response(200, CarSchema(many=True))
    def get(self):
        cars = Car.query.all()
        return cars

    @bp.arguments(deleteCarSchema)
    def delete(self,args):
        car_id = args['id']
        car = Car.query.get_or_404(car_id)
        db.session.delete(car)
        db.session.commit()
        return {"message": "Car deleted"}

    @bp.arguments(CarSchema)
    @bp.response(201, CarSchema)
    def post(self, car_data):
        new_car=Car(**car_data)
        try:
            db.session.add(new_car)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the car.")
        return new_car
