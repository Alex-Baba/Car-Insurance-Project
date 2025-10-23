from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from app.api.schemas import ClaimCreate, ClaimOut
from app.services.claim_service import list_claims, create_claim

def _to_json(c):
    return ClaimOut.model_validate(c).model_dump(by_alias=False)

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@claims_bp.route('/')
class ClaimsCollection(MethodView):
    def get(self):
        claims = list_claims()
        return [ClaimOut.model_validate(c, from_attributes=True).model_dump(by_alias=False) for c in claims], 200

    def post(self):
        data = request.get_json(force=True, silent=True) or {}
        try:
            body = ClaimCreate.model_validate(data)
        except Exception as e:
            if hasattr(e, "errors"):
                errs = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
                return {"status": 422, "title": "Validation Error", "errors": errs}, 422
            return {"status": 400, "title": "Bad Request", "detail": str(e)}, 400
        c = create_claim(body.claimDate, body.description, body.amount, body.carId)
        return ClaimOut.model_validate(c, from_attributes=True).model_dump(by_alias=False), 201