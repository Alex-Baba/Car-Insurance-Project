from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint

from app.db.models import Car
from app.api.schemas import CarSchema

bp = Blueprint('cars', __name__, url_prefix='/api/cars')

@bp.route('/')
class CarsResource(MethodView):
    @bp.response(200, CarSchema(many=True))
    def get(self):
        cars = Car.query.all()
        return cars
