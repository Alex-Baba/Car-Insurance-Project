from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from pydantic import ValidationError
from app.api.schemas import OwnerCreate, OwnerOut
from app.services.owners_service import list_owners, create_owner
from app.api.errors import DomainValidationError

owner_bp = Blueprint('owners', __name__, url_prefix='/api/owners')

@owner_bp.route('/')
class OwnersResource(MethodView):
    def get(self):
        owners = list_owners()
        return [OwnerOut.model_validate(o, from_attributes=True).model_dump(by_alias=True) for o in owners], 200

    def post(self):
        data = request.get_json(force=True, silent=True) or {}
        try:
            body = OwnerCreate.model_validate(data)
        except ValidationError as ve:
            raise DomainValidationError("Invalid owner payload", field="body")
        owner = create_owner(body.model_dump())
        out = OwnerOut.model_validate(owner, from_attributes=True)
        return out.model_dump(by_alias=True), 201
