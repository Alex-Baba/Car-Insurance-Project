from flask import Blueprint, jsonify, request
bp = Blueprint('policies', __name__, url_prefix='/api/cars/<int:car_id>/policies')
@bp.post('/')  # http://127.0.0.1:5000/api/cars/<car_id>/policies
def create_policy(car_id):
    policy_data = request.get_json()
    for store in stores:
        if store['name'] == 'api':
            for car in store['cars']:
                if car['id'] == car_id:
                    new_policy = {
                        "policyId": len(car.get('policies', [])) + 1,
                        "policyNumber": policy_data.get('policyNumber'),
                        "startDate": policy_data.get('startDate'),
                        "endDate": policy_data.get('endDate'),
                        "premium": policy_data.get('premium')
                    }
                    car.setdefault('policies', []).append(new_policy)
                    return jsonify(new_policy), 201
    return jsonify({'message': 'car not found'}), 404