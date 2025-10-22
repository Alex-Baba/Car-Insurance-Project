from flask.views import MethodView
from flask_smorest import Blueprint
from flask_pydantic import validate
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

    @validate()
    def post(self, body: PolicyCreate):
        p = create_policy(body.provider, body.startDate, body.endDate, body.carId)
        return _to_json(p), 201

@policies_bp.route('/<int:policy_id>')
class InsurancePolicyItem(MethodView):
    def get(self, policy_id: int):
        p = get_policy(policy_id)
        return _to_json(p), 200

    @validate()
    def put(self, policy_id: int, body: PolicyUpdate):
        p = update_policy(
            policy_id,
            provider=body.provider,
            start_date=body.startDate,
            end_date=body.endDate
        )
        return _to_json(p), 200
