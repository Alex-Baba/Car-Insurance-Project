from flask import Flask, jsonify, request
from flask_smorest import Blueprint
from flask.views import MethodView

from api.schemas import CarSchema

bp=Blueprint('cars', __name__)

@bp.route('/api/cars')
class Car(MethodView):
    @bp.response(200, CarSchema(many=True))
    def get(self):
        return Cars.values()
