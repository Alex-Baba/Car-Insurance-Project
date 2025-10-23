from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request
from app.db.models import InsurancePolicy
from app.api.schemas import PolicyCreate, PolicyUpdate
from app.services.policies_service import list_policies, create_policy, update_policy, get_policy

policies_bp = Blueprint('policies', __name__, url_prefix='/api/cars/policies')

def _to_json(p: InsurancePolicy):
    return {
        "id": p.id,
        "provider": p.provider,
        "startDate": p.start_date.isoformat(),
        "endDate": p.end_date.isoformat(),
        "carId": p.car_id
    }

@policies_bp.route('/')
class InsurancePolicyAPI(MethodView):
    def get(self):
        return [_to_json(p) for p in list_policies()], 200

    def post(self):
        data = request.get_json(force=True, silent=True) or {}
        try:
            body = PolicyCreate.model_validate(data)
        except Exception as e:
            if hasattr(e, "errors"):
                errs = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
                return {"status": 422, "title": "Validation Error", "errors": errs}, 422
            return {"status": 400, "title": "Bad Request", "detail": str(e)}, 400
        p = create_policy(body.provider, body.startDate, body.endDate, body.carId)
        return _to_json(p), 201

@policies_bp.route('/<int:policy_id>')
class InsurancePolicyItem(MethodView):
    def get(self, policy_id: int):
        p = get_policy(policy_id)
        return _to_json(p), 200

    def put(self, policy_id: int):
        data = request.get_json(force=True, silent=True) or {}
        try:
            body = PolicyUpdate.model_validate(data)
        except Exception as e:
            if hasattr(e, "errors"):
                errs = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
                return {"status": 422, "title": "Validation Error", "errors": errs}, 422
            return {"status": 400, "title": "Bad Request", "detail": str(e)}, 400
        p = update_policy(
            policy_id,
            provider=body.provider,
            start_date=body.startDate,
            end_date=body.endDate
        )
        return _to_json(p), 200
