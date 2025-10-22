from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import and_
from app.db.models import InsurancePolicy, Car
from app.api.schemas import InsuranceValiditySchema

insurance_validation_bp = Blueprint(
    'insurance_validation',
    __name__,
    url_prefix='/api/cars'
)

@insurance_validation_bp.route('/<int:car_id>/insurance-valid')
class InsuranceValidResource(MethodView):
    @insurance_validation_bp.response(200, InsuranceValiditySchema)
    def get(self, car_id):
        car = Car.query.get(car_id)
        if not car:
            abort(404, message="Car not found")

        date_str = request.args.get('date')
        if not date_str:
            abort(400, message="Missing ?date=YYYY-MM-DD")

        # Use schema to validate/parse the date
        schema = InsuranceValiditySchema()
        try:
            parsed = schema.load({"carId": car_id, "date": date_str, "valid": False})
        except Exception as e:
            abort(400, message=str(e))

        d = parsed["date"]

        policy = InsurancePolicy.query.filter(
            and_(
                InsurancePolicy.car_id == car_id,
                InsurancePolicy.start_date <= d,
                InsurancePolicy.end_date >= d
            )
        ).first()

        parsed["valid"] = bool(policy)
        return parsed