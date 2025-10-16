from flask import Blueprint, jsonify,request

health_bp = Blueprint('health', __name__, url_prefix='/')

@health_bp.route('/health') #http://127.0.0.1:5000/health
def health_check():
    return jsonify({'status': 'healthy'}), 200