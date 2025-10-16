from flask import Flask, jsonify, request, Blueprint

bp=Blueprint('cars', __name__, url_prefix='/api/cars')


@bp.get('/') #http://127.0.0.1:5000/api/cars
def get_cars():
    for store in stores:
        if store['name'] == 'api':
            return jsonify(store['cars']), 200
    return jsonify({'message': 'car not found'}), 404