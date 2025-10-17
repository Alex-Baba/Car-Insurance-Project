from flask import jsonify
from flask_smorest import Blueprint

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200