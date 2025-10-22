from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import ValidationError
from app.db.models import InsurancePolicy, Car
from app.api.schemas import InsuranceValiditySchema
from app.api.errors import NotFoundError
from flask import request

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
            raise NotFoundError("Car not found")

        date_str = request.args.get('date')
        if not date_str:
            raise ValidationError({"date": ["Missing query parameter 'date'"]})

        schema = InsuranceValiditySchema()
        parsed = schema.load({"carId": car_id, "date": date_str, "valid": False})

        d = parsed["date"]
        policy = InsurancePolicy.query.filter(
            InsurancePolicy.car_id == car_id,
            InsurancePolicy.start_date <= d,
            InsurancePolicy.end_date >= d
        ).first()

        parsed["valid"] = bool(policy)
        return parsed