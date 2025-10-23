from flask.views import MethodView
from flask_smorest import Blueprint
from app.services.history_service import car_history
from app.api.schemas import HistoryEntryOut

history_bp = Blueprint('history', __name__, url_prefix='/api/history', description='History resource: unified chronological timeline of policies and claims for a car.')

@history_bp.route('/<int:car_id>')
class CarHistoryResource(MethodView):
    """Retrieve chronological policy/claim history for a single car."""
    def get(self, car_id):
        """Return sorted merged entries (ISO date strings)."""
        entries = car_history(car_id)
        # entries are dicts already; validate each through pydantic for consistency
        validated = [HistoryEntryOut.model_validate(e).model_dump(by_alias=True) for e in entries]
        return validated, 200