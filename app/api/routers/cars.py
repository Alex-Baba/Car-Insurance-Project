from flask import Flask, jsonify, request, Blueprint
from flask.views import MethodView

bp=Blueprint('cars', __name__,description="Cars related operations")


bp.route('/api/cars')
class Car(MethodView):
    def get(self,name):
        for store in stores:
            if store['name'] == name:
                return jsonify(store), 200
        return jsonify({'message': 'car not found'}), 404