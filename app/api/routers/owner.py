from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from pydantic import ValidationError
from app.api.schemas import OwnerCreate, OwnerOut
from app.services.owners_service import list_owners, create_owner
from app.api.errors import DomainValidationError

owner_bp = Blueprint('owners', __name__, url_prefix='/api/owners', description='Owners resource: list and create owners; future item endpoint will allow retrieval.')

@owner_bp.route('/')
class OwnersResource(MethodView):
    """List existing owners or create new ones."""
    def get(self):
        """Return all owners serialized with OwnerOut."""
        owners = list_owners()
        return [OwnerOut.model_validate(o, from_attributes=True).model_dump(by_alias=True) for o in owners], 200

    def post(self):
        """Create a new owner.

        Parses JSON, validates via OwnerCreate, then persists using service layer.
        Returns (owner_json, 201).
        """
        data = request.get_json(force=True, silent=True) or {}
        try:
            body = OwnerCreate.model_validate(data)
        except ValidationError:
            raise DomainValidationError("Invalid owner payload", field="body")
        owner = create_owner(body.model_dump())
        out = OwnerOut.model_validate(owner, from_attributes=True)
        return out.model_dump(by_alias=True), 201
