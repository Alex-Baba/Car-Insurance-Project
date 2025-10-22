from app.db.base import datab as db
from app.db.models import Claims, Car
from app.api.schemas import ClaimsSchema
from app.api.errors import NotFoundError
from flask.views import MethodView
from flask_smorest import Blueprint

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@claims_bp.route('/')
class ClaimsResource(MethodView):
    @claims_bp.response(200, ClaimsSchema(many=True))
    def get(self):
        return Claims.query.all()

    @claims_bp.arguments(ClaimsSchema)
    @claims_bp.response(201, ClaimsSchema)
    def post(self, data):
        car = Car.query.get(data["car_id"])
        if not car:
            raise NotFoundError("Car not found")
        claim = Claims(**data)
        db.session.add(claim)
        db.session.commit()
        return claim