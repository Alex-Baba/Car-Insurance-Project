from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_pydantic import validate
from app.api.schemas import ClaimCreate, ClaimsSchema
from app.services.claim_service import list_claims, create_claim

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@claims_bp.route('/')
class ClaimsCollection(MethodView):
    @claims_bp.response(200, ClaimsSchema(many=True))
    def get(self):
        return list_claims()

    @validate()
    @claims_bp.response(201, ClaimsSchema)
    def post(self, body: ClaimCreate):
        return create_claim(body.claimDate, body.description, body.amount, body.carId)