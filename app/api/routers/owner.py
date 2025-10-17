from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import Owner
from app.api.schemas import OwnerSchema

from app.db.base import datab as db

owner_bp = Blueprint('owners', __name__, url_prefix='/api/owners')

@owner_bp.route('/')
class OwnersResource(MethodView):
    @owner_bp.response(200, OwnerSchema(many=True))
    def get(self):
        owners = Owner.query.all()
        return owners

    @owner_bp.arguments(OwnerSchema)
    @owner_bp.response(201, OwnerSchema)
    def post(self, owner_data):
        new_owner = Owner(**owner_data)
        db.session.add(new_owner)
        db.session.commit()
        return new_owner
