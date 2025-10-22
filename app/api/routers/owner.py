from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint
from app.api.schemas import OwnerSchema
from app.services.owners_service import list_owners, create_owner

owner_bp = Blueprint('owners', __name__, url_prefix='/api/owners')

@owner_bp.route('/')
class OwnersResource(MethodView):
    @owner_bp.response(200, OwnerSchema(many=True))
    def get(self):
        return list_owners()

    @owner_bp.arguments(OwnerSchema)
    @owner_bp.response(201, OwnerSchema)
    def post(self, owner_data):
        return create_owner(owner_data)
