from flask import Blueprint, jsonify, request

bp = Blueprint('history', __name__, url_prefix='/api/cars/<int:car_id>/history')

@bp.get('/')  # http://127.0.0.1:5000/api/cars/<car_id>/history
def get_history(car_id):
    for store in stores:
        if store['name'] == 'api':
            for car in store['cars']:
                if car['id'] == car_id:
                    return jsonify(car['policies'], car['claims']), 200
    return jsonify({'message': 'car not found'}), 404