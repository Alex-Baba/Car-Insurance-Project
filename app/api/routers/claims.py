from app.db.base import datab as db
from app.db.models import Claims
from app.api.schemas import ClaimsSchema

from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@claims_bp.route('/')
class ClaimsResource(MethodView):
    @claims_bp.response(200, ClaimsSchema(many=True))
    def get(self):
        claims = Claims.query.all()
        return claims

    @claims_bp.arguments(ClaimsSchema)
    @claims_bp.response(201, ClaimsSchema)
    def post(self, claim_data):
        new_claim = Claims(**claim_data)
        db.session.add(new_claim)
        db.session.commit()
        return new_claim