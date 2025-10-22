from app.db.base import datab as db
from app.db.models import InsurancePolicy, Car
from app.api.schemas import InsurancePolicySchema
from app.api.errors import NotFoundError
from flask.views import MethodView
from flask_smorest import Blueprint

policies_bp = Blueprint('policies', __name__, url_prefix='/api/cars/policies')

@policies_bp.route('/')
class InsurancePolicyAPI(MethodView):
    @policies_bp.response(200, InsurancePolicySchema(many=True))
    def get(self):
        return InsurancePolicy.query.all()

    @policies_bp.arguments(InsurancePolicySchema)
    @policies_bp.response(201, InsurancePolicySchema)
    def post(self, data):
        car = Car.query.get(data["car_id"])
        if not car:
            raise NotFoundError("Car not found")
        policy = InsurancePolicy(**data)
        db.session.add(policy)
        db.session.commit()
        return policy
