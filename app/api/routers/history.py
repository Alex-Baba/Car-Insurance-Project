from app.db.base import datab as db
from app.db.models import InsurancePolicy, Claims, Car
from app.api.schemas import HistoryEntrySchema
from app.api.errors import NotFoundError
from flask.views import MethodView
from flask_smorest import Blueprint
from app.services.history_service import car_history

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

@history_bp.route('/<int:car_id>')
class CarHistoryResource(MethodView):
    @history_bp.response(200, HistoryEntrySchema(many=True))
    def get(self, car_id):
        return car_history(car_id)