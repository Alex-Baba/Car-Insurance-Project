from flask import jsonify, request
from flask_smorest import Blueprint

bp = Blueprint('claims', __name__, url_prefix='/api/cars/<int:car_id>/claims')

@bp.post('/')  # http://127.0.0.1:5000/api/cars/<car_id>/claims
def create_claim(car_id):
    claim_data = request.get_json()
    for store in stores:
        if store['name'] == 'api':
            for car in store['cars']:
                if car['id'] == car_id:
                    new_claim = {
                        "claimId": len(car.get('claims', [])) + 1,
                        "claimDate": claim_data.get('claimDate'),
                        "amount": claim_data.get('amount'),
                        "description": claim_data.get('description')
                    }
                    car.setdefault('claims', []).append(new_claim)
                    return jsonify(new_claim), 201
    return jsonify({'message': 'car not found'}), 404