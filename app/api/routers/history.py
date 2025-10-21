from app.db.base import datab as db
from app.db.models import InsurancePolicy, Claims, Car
from app.api.schemas import HistoryEntrySchema
from flask.views import MethodView
from flask_smorest import Blueprint, abort

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

@history_bp.route('/<int:car_id>')
class CarHistoryResource(MethodView):
    @history_bp.response(200, HistoryEntrySchema(many=True))
    def get(self, car_id):
        car = Car.query.get(car_id)
        if not car:
            abort(404, message="Car not found")

        policies = InsurancePolicy.query.filter_by(car_id=car_id).all()
        claims = Claims.query.filter_by(car_id=car_id).all()

        entries = []
        for p in policies:
            entries.append({
                "type": "POLICY",
                "policyId": p.id,
                "startDate": p.start_date,
                "endDate": p.end_date,
                "provider": p.provider
            })
        for c in claims:
            entries.append({
                "type": "CLAIM",
                "claimId": c.id,
                "claimDate": c.claim_date,
                "amount": getattr(c, "amount", None),
                "description": getattr(c, "description", None)
            })

        def sort_key(e):
            return e.get("startDate") or e.get("claimDate") or e.get("endDate")
        entries.sort(key=sort_key)
        return entries