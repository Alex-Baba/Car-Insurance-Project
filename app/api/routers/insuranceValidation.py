from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import ValidationError
from flask import request
from app.api.schemas import InsuranceValiditySchema
from app.services.validity_service import check_insurance

insurance_validation_bp = Blueprint(
    'insurance_validation',
    __name__,
    url_prefix='/api/cars'
)

@insurance_validation_bp.route('/<int:car_id>/insurance-valid')
class InsuranceValidResource(MethodView):
    @insurance_validation_bp.response(200, InsuranceValiditySchema)
    def get(self, car_id):
        date_str = request.args.get('date')
        if not date_str:
            raise ValidationError({"date": ["Missing query parameter 'date'"]})
        schema = InsuranceValiditySchema()
        parsed = schema.load({"carId": car_id, "date": date_str, "valid": False})
        d = parsed["date"]
        valid, policy = check_insurance(car_id, d)
        parsed["valid"] = valid
        return parsed