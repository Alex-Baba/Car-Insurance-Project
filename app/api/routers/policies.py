from app.db.base import datab as db
from app.db.models import InsurancePolicy, Car
from app.api.schemas import InsurancePolicySchema
from app.api.errors import NotFoundError
from flask.views import MethodView
from flask_smorest import Blueprint
from app.services.policies_service import list_policies, create_policy

policies_bp = Blueprint('policies', __name__, url_prefix='/api/cars/policies')

@policies_bp.route('/')
class InsurancePolicyAPI(MethodView):
    @policies_bp.response(200, InsurancePolicySchema(many=True))
    def get(self):
        return list_policies()

    @policies_bp.arguments(InsurancePolicySchema)
    @policies_bp.response(201, InsurancePolicySchema)
    def post(self, data):
        return create_policy(data)
