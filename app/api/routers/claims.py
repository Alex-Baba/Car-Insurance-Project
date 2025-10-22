from flask.views import MethodView
from flask_smorest import Blueprint
from app.api.schemas import ClaimsSchema
from app.services.claim_service import list_claims, create_claim

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@claims_bp.route('/')
class ClaimsResource(MethodView):
    @claims_bp.response(200, ClaimsSchema(many=True))
    def get(self):
        return list_claims()

    @claims_bp.arguments(ClaimsSchema)
    @claims_bp.response(201, ClaimsSchema)
    def post(self, data):
        return create_claim(data)