from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request
from pydantic import ValidationError
from app.api.schemas import InsuranceValiditySchema
from app.db.models import InsuranceValidityQuery
from app.services.validity_service import check_insurance

insurance_validation_bp = Blueprint('insurance_validation', __name__, url_prefix='/api/cars')

@insurance_validation_bp.route('/<int:car_id>/insurance-valid')
class InsuranceValidResource(MethodView):
    @insurance_validation_bp.response(200, InsuranceValiditySchema)
    def get(self, car_id):
        date_str = request.args.get("date")
        if not date_str:
            raise ValidationError.from_exception_data("date", [{
                "loc": ("date",),
                "msg": "Missing query parameter 'date'",
                "type": "value_error.missing"
            }])
        model = InsuranceValidityQuery(carId=car_id, date=date_str)
        result = check_insurance(model.carId, model.date)
        # Marshmallow schema will serialize date
        return result, 200