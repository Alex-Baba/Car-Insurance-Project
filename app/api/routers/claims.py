from flask import request, url_for
from flask.views import MethodView
from flask_smorest import Blueprint
from app.api.schemas import ClaimCreate, ClaimOut
from app.services.claim_service import list_claims, create_claim, get_claims_for_car, get_claim
from app.api.errors import NotFoundError

def _to_json(c):
    return ClaimOut.model_validate(c, from_attributes=True).model_dump(by_alias=False)

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims', description='Claims resource: create, list, retrieve and delete insurance claims associated with cars.')

@claims_bp.route('/')
class ClaimsCollection(MethodView):
    """Collection resource for listing all claims or creating a new one."""
    def get(self):
        """Return all claims."""
        claims = list_claims()
        return [ClaimOut.model_validate(c, from_attributes=True).model_dump(by_alias=False) for c in claims], 200

    def post(self):
        """Validate and create a new claim for a car."""
        data = request.get_json(force=True, silent=True) or {}
        try:
            body = ClaimCreate.model_validate(data)
        except Exception as e:
            if hasattr(e, "errors"):
                errs = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
                return {"status": 422, "title": "Validation Error", "errors": errs}, 422
            return {"status": 400, "title": "Bad Request", "detail": str(e)}, 400
        try:
            c = create_claim(body.claimDate, body.description, body.amount, body.carId)
        except NotFoundError as nf:
            return {"status": 404, "title": "Not Found", "detail": nf.message}, 404
        except Exception as e:
            return {"status": 500, "title": "Internal Server Error", "detail": str(e)}, 500
        data_out = ClaimOut.model_validate(c, from_attributes=True).model_dump(by_alias=False)
        headers = {'Location': f"/api/claims/{c.id}"}
        return data_out, 201, headers

@claims_bp.route('/<int:claim_id>')
class ClaimItem(MethodView):
    """Item resource for a single claim."""
    def get(self, claim_id: int):
        c = get_claim(claim_id)
        return ClaimOut.model_validate(c, from_attributes=True).model_dump(by_alias=False), 200

    def delete(self, claim_id: int):
        from app.services.claim_service import delete_claim
        delete_claim(claim_id)
        return "", 204

# Nested car claims collection
@claims_bp.route('/car/<int:car_id>')
class CarClaimsCollection(MethodView):
    """List or create claims nested under a car resource."""
    def get(self, car_id: int):
        claims = get_claims_for_car(car_id)
        return [ClaimOut.model_validate(c, from_attributes=True).model_dump(by_alias=False) for c in claims], 200

    def post(self, car_id: int):
        data = request.get_json(force=True, silent=True) or {}
        # Allow body to omit carId when nested
        if 'carId' not in data:
            data['carId'] = car_id
        try:
            body = ClaimCreate.model_validate(data)
        except Exception as e:
            if hasattr(e, "errors"):
                errs = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
                return {"status": 422, "title": "Validation Error", "errors": errs}, 422
            return {"status": 400, "title": "Bad Request", "detail": str(e)}, 400
        try:
            c = create_claim(body.claimDate, body.description, body.amount, body.carId)
        except NotFoundError as nf:
            return {"status": 404, "title": "Not Found", "detail": nf.message}, 404
        except Exception as e:
            return {"status": 500, "title": "Internal Server Error", "detail": str(e)}, 500
        data_out = ClaimOut.model_validate(c, from_attributes=True).model_dump(by_alias=False)
        headers = {'Location': f"/api/claims/{c.id}"}
        return data_out, 201, headers