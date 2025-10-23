from flask.views import MethodView
from flask_smorest import Blueprint
from app.services.history_service import car_history
from app.api.schemas import HistoryEntryOut

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

@history_bp.route('/<int:car_id>')
class CarHistoryResource(MethodView):
    def get(self, car_id):
        entries = car_history(car_id)
        # entries are dicts already; validate each through pydantic for consistency
        validated = [HistoryEntryOut.model_validate(e).model_dump(by_alias=True) for e in entries]
        return validated, 200