from app.db.base import datab as db
from app.db.models import InsurancePolicy
from app.api.schemas import InsurancePolicySchema
from flask.views import MethodView
from flask import Flask, jsonify, request
from flask_smorest import Blueprint
from marshmallow import ValidationError

policies_bp = Blueprint('policies', __name__, url_prefix='/api/cars/policies')

@policies_bp.route('/')
class InsurancePolicyAPI(MethodView):
    @policies_bp.response(200, InsurancePolicySchema(many=True))
    def get(self):
        policies = InsurancePolicy.query.all()
        return policies

    @policies_bp.arguments(InsurancePolicySchema)
    @policies_bp.response(201, InsurancePolicySchema)
    def post(self, policies_data):
        new_policy = InsurancePolicy(**policies_data)
        db.session.add(new_policy)
        db.session.commit()
        return new_policy
