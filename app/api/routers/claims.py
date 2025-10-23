from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request
from app.api.schemas import ClaimCreate, ClaimsSchema, ClaimOut
from app.services.claim_service import list_claims, create_claim

def _to_json(c):
    return ClaimOut.model_validate(c).model_dump(by_alias=False)

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@claims_bp.route('/')
class ClaimsCollection(MethodView):
    @claims_bp.response(200, ClaimsSchema(many=True))
    def get(self):
        return list_claims()

    @claims_bp.response(201, ClaimsSchema)
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
        return c