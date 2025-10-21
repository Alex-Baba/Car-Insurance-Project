from app.db.base import datab as db
from app.api.schemas import HistorySchema
from app.db.models import InsurancePolicy, Claims
from flask.views import MethodView
from flask_smorest import Blueprint

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

@history_bp.route('/')
class HistoryResource(MethodView):
    @history_bp.response(200, HistorySchema)
    def get(self):
        policies = InsurancePolicy.query.all()
        claims = Claims.query.all()
        return {"policies": policies, "claims": claims}